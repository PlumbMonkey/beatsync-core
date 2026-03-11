"""
Minimal FastAPI backend for BeatSync Studio Slice 4.1
Satisfies test_api_analysis.py contract tests
"""
import os
import tempfile
import uuid
import hashlib
import json
import sys
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from jsonschema import validate, ValidationError
from beatsync_core.core import audio as beatsync_audio
from beatsync_core.core import midi as beatsync_midi

# --- Config ---
ACCEPTED_EXTS = {".wav", ".mp3", ".flac", ".ogg", ".mid"}
SCHEMA_VERSION = "0.1"
ANALYSIS_VERSION = "0.1.0"
DEPLOY_VERSION = "2026-03-11-v3"  # Bump on each deploy to verify code freshness
STORAGE_ROOT = "storage"  # relative to project root

# Resolve schema path - works in both local dev and Render deployment
SCHEMA_PATH = None
# Try 1: Local monorepo structure (local dev)
local_schema = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../beatsync-core/schema/v0_1.json'))
if os.path.exists(local_schema):
    SCHEMA_PATH = local_schema
# Try 2: Installed package structure (Render)
else:
    try:
        import beatsync_core
        package_dir = os.path.dirname(beatsync_core.__file__)
        pkg_schema = os.path.join(package_dir, '..', 'schema', 'v0_1.json')
        if os.path.exists(pkg_schema):
            SCHEMA_PATH = os.path.abspath(pkg_schema)
    except (ImportError, AttributeError):
        pass

if not SCHEMA_PATH:
    raise RuntimeError("Schema file not found at expected locations. Check beatsync-core installation.")

# Load canonical schema once
with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
    CANONICAL_SCHEMA = json.load(f)

# Confirm schema loaded at startup
print(f"SCHEMA LOADED FROM: {SCHEMA_PATH}", file=sys.stderr, flush=True)
print(f"SCHEMA KEYS: {list(CANONICAL_SCHEMA.keys())}", file=sys.stderr, flush=True)

# --- App & Router ---
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://beatsync-ui.vercel.app",
        "http://localhost:5173",  # Vite dev server
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Root & Health — registered directly on app (not via router) ---
@app.get("/")
async def root():
    return {
        "service": "beatsync-studio",
        "version": ANALYSIS_VERSION,
        "deploy": DEPLOY_VERSION,
        "docs": "/docs"
    }

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "beatsync-studio"}

router = APIRouter()

# --- Helpers ---
def get_ext(filename):
    return os.path.splitext(filename)[1].lower()

def compute_analysis_hash(file_bytes, core_version, schema_version):
    h = hashlib.sha256()
    h.update(file_bytes)
    h.update(core_version.encode())
    h.update(schema_version.encode())
    return f"sha256:{h.hexdigest()}"


def extract_contract_fields(result):
    # Map canonical output to contract fields required by tests
    # (schema_version, analysis_version, duration_sec, bpm, confidence)
    # The schema nests these under metadata, tempo, key
    return {
        "schema_version": SCHEMA_VERSION,
        "analysis_version": result["metadata"]["analysis_version"],
        "duration_sec": result["metadata"]["duration_sec"],
        "bpm": result["tempo"]["bpm"],
        "confidence": {
            "tempo": result["tempo"]["confidence"],
            "key": result["key"]["confidence"]
        }
    }

# --- Endpoint ---
@router.post("/api/analysis")
async def analyze(file: UploadFile = File(...)):
    # Step 1: Validate file presence and extension
    if not file:
        raise HTTPException(status_code=400, detail="Missing file")
    ext = get_ext(file.filename)
    if ext not in ACCEPTED_EXTS:
        raise HTTPException(status_code=400, detail="Unsupported file format")
    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Empty file")
    # Step 2: Temp file handling
    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = os.path.abspath(os.path.join(tmpdir, f"input{ext}"))
        with open(input_path, "wb") as f:
            f.write(file_bytes)
        # Step 3: BeatSync Core invocation (direct Python call)
        try:
            if ext in [".wav", ".mp3", ".flac", ".ogg"]:
                result = beatsync_audio.analyze(input_path)
            elif ext in [".mid", ".midi"]:
                result = beatsync_midi.analyze(input_path)
            else:
                raise ValueError(f"Unsupported file type: {ext}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"BeatSync Core failed: {str(e)}")
        # Step 4: Schema validation
        print("ANALYSIS RESULT:", json.dumps(result, indent=2, default=str), file=sys.stderr, flush=True)
        try:
            validate(instance=result, schema=CANONICAL_SCHEMA)
        except ValidationError as e:
            print(f"SCHEMA PATH: {list(e.path)}", file=sys.stderr, flush=True)
            print(f"SCHEMA MESSAGE: {e.message}", file=sys.stderr, flush=True)
            print(f"SCHEMA VALIDATOR: {e.validator}", file=sys.stderr, flush=True)
            print(f"FAILED VALUE: {e.instance}", file=sys.stderr, flush=True)
            raise HTTPException(status_code=422, detail="Schema validation failed")
        # Step 5: Deterministic hash
        analysis_hash = compute_analysis_hash(file_bytes, result["metadata"]["analysis_version"], SCHEMA_VERSION)
        analysis_id = str(uuid.uuid4())
        # Step 6: Persistence (no user_id, just hash)
        out_dir = os.path.abspath(os.path.join(STORAGE_ROOT, analysis_hash))
        os.makedirs(out_dir, exist_ok=True)
        out_json = os.path.join(out_dir, "beatsync.json")
        # Only persist if not already present (determinism)
        if not os.path.exists(out_json):
            with open(out_json, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2)
        # Step 7: Response shape
        contract = extract_contract_fields(result)
        resp = {
            "analysis_id": analysis_id,
            "analysis_hash": analysis_hash,
            **contract,
            "download_url": f"/api/analysis/{analysis_id}/download"
        }
        # Remove forbidden fields if present
        for forbidden in ("_debug", "_mutation", "_internal"):
            resp.pop(forbidden, None)
        return JSONResponse(resp)

app.include_router(router)
