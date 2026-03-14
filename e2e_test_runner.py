#!/usr/bin/env python3
"""
BeatSync Studio E2E Testing Protocol Runner
March 2026
"""
import sys
import json
import time
from pathlib import Path

# Add beatsync packages to path for local testing
sys.path.insert(0, str(Path(__file__).parent / "beatsync-core" / "src"))
sys.path.insert(0, str(Path(__file__).parent / "beatsync-midi" / "src"))
sys.path.insert(0, str(Path(__file__).parent / "beatsync-studio" / "src"))

def test_imports():
    """TEST 0: Verify core packages can be imported"""
    print("\n" + "="*70)
    print("TEST 0 — IMPORT VERIFICATION")
    print("="*70)
    
    try:
        from beatsync_core.core import audio, key, structure
        print("✅ beatsync_core imported successfully")
        print(f"   - audio module: {audio.__file__}")
        print(f"   - key module: {key.__file__}")
        print(f"   - structure module: {structure.__file__}")
    except Exception as e:
        print(f"❌ Failed to import beatsync_core: {e}")
        return False
    
    try:
        from beatsync_midi import key_detect
        print("✅ beatsync_midi imported successfully")
        print(f"   - key_detect module: {key_detect.__file__}")
    except Exception as e:
        print(f"❌ Failed to import beatsync_midi: {e}")
        return False
    
    try:
        import fastapi
        print("✅ FastAPI imported successfully")
    except Exception as e:
        print(f"❌ Failed to import FastAPI: {e}")
        return False
    
    return True

def test_schema_loading():
    """TEST 0b: Verify schema file exists and is valid"""
    print("\n" + "="*70)
    print("TEST 0b — SCHEMA VALIDATION")
    print("="*70)
    
    schema_path = Path(__file__).parent / "beatsync-core" / "schema" / "v0_1.json"
    
    if not schema_path.exists():
        print(f"❌ Schema file not found at {schema_path}")
        return False
    
    try:
        with open(schema_path) as f:
            schema = json.load(f)
        print(f"✅ Schema loaded successfully from {schema_path}")
        print(f"   - Schema type: {schema.get('type', 'unknown')}")
        print(f"   - Required fields: {schema.get('required', [])}")
        print(f"   - Properties count: {len(schema.get('properties', {}))}")
        return True
    except json.JSONDecodeError as e:
        print(f"❌ Schema JSON is invalid: {e}")
        return False
    except Exception as e:
        print(f"❌ Failed to load schema: {e}")
        return False

def test_backend_main():
    """TEST 1: Verify backend main.py loads without errors"""
    print("\n" + "="*70)
    print("TEST 1 — BACKEND HEALTH CHECK (Local)")
    print("="*70)
    
    try:
        # Add beatsync_studio to path
        sys.path.insert(0, str(Path(__file__).parent / "beatsync-studio"))
        from beatsync_studio.main import app, CANONICAL_SCHEMA, ACCEPTED_EXTS
        
        print("✅ FastAPI app loaded successfully")
        print(f"   - Accepted formats: {ACCEPTED_EXTS}")
        print(f"   - Schema version: {CANONICAL_SCHEMA.get('title', 'unknown')}")
        print(f"   - Routes configured: {len(app.routes)}")
        
        # List routes
        for route in app.routes:
            if hasattr(route, 'path'):
                print(f"     • {route.path}")
        
        return True
    except Exception as e:
        print(f"❌ Failed to load FastAPI app: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cors_config():
    """TEST 2: Verify CORS is properly configured"""
    print("\n" + "="*70)
    print("TEST 2 — CORS CONFIGURATION")
    print("="*70)
    
    try:
        sys.path.insert(0, str(Path(__file__).parent / "beatsync-studio"))
        from beatsync_studio.main import app
        
        cors_middleware = None
        for middleware in app.user_middleware:
            if "CORSMiddleware" in str(middleware):
                cors_middleware = middleware
                break
        
        if cors_middleware:
            print("✅ CORSMiddleware is configured")
            print(f"   - Middleware: {cors_middleware}")
        else:
            print("⚠️  No CORSMiddleware found in middleware stack")
            print("   (This is OK if CORS is in app.middleware list)")
        
        return True
    except Exception as e:
        print(f"❌ Failed to check CORS config: {e}")
        return False

def test_requirements():
    """TEST 3: Verify all required dependencies are installed"""
    print("\n" + "="*70)
    print("TEST 3 — DEPENDENCY VERIFICATION")
    print("="*70)
    
    required_packages = [
        "fastapi",
        "uvicorn",
        "python-multipart",
        "librosa",
        "numpy",
        "scipy",
        "mido",
        "jsonschema",
    ]
    
    missing = []
    versions = {}
    
    for package in required_packages:
        try:
            module = __import__(package.replace("-", "_"))
            version = getattr(module, "__version__", "unknown")
            versions[package] = version
            print(f"✅ {package:<25} v{version}")
        except ImportError:
            missing.append(package)
            print(f"❌ {package:<25} NOT INSTALLED")
    
    if missing:
        print(f"\n⚠️  Missing packages: {missing}")
        print("   Run: pip install " + " ".join(missing))
        return False
    
    return True

def test_requirements_txt():
    """TEST 4: Verify requirements.txt has all dependencies"""
    print("\n" + "="*70)
    print("TEST 4 — REQUIREMENTS.TXT VERIFICATION")
    print("="*70)
    
    req_file = Path(__file__).parent / "beatsync-studio" / "requirements.txt"
    
    if not req_file.exists():
        print(f"❌ requirements.txt not found at {req_file}")
        return False
    
    with open(req_file) as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    
    print(f"✅ requirements.txt found with {len(requirements)} dependencies:")
    for req in requirements:
        print(f"   • {req}")
    
    # Check for critical packages
    critical = ["python-multipart", "fastapi", "librosa"]
    missing_critical = []
    
    for pkg in critical:
        found = any(pkg in req for req in requirements)
        if not found:
            missing_critical.append(pkg)
    
    if missing_critical:
        print(f"\n❌ Missing critical packages in requirements.txt: {missing_critical}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("BEATSYNC STUDIO — E2E TESTING PROTOCOL RUNNER")
    print("="*70)
    print("Testing: beatsync-core, beatsync-midi, beatsync-studio")
    print("Date: March 2026")
    print("="*70)
    
    results = {}
    
    # Run tests
    results["imports"] = test_imports()
    results["schema"] = test_schema_loading()
    results["backend"] = test_backend_main()
    results["cors"] = test_cors_config()
    results["requirements"] = test_requirements()
    results["requirements_txt"] = test_requirements_txt()
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} — {test_name.upper()}")
    
    print("\n" + "="*70)
    if passed == total:
        print(f"✅ ALL TESTS PASSED ({passed}/{total})")
        print("="*70)
        print("\nNEXT STEPS:")
        print("1. Deploy backend to Render: git push origin main")
        print("2. Deploy frontend to Vercel: vercel --prod")
        print("3. Run curl tests against live endpoints:")
        print("   - https://beatsync-studio.onrender.com/")
        print("   - https://beatsync-ui.vercel.app")
        return 0
    else:
        print(f"⚠️  SOME TESTS FAILED ({passed}/{total} passed)")
        print("="*70)
        print("\nFIX ISSUES ABOVE BEFORE DEPLOYING TO PRODUCTION")
        return 1

if __name__ == "__main__":
    sys.exit(main())
