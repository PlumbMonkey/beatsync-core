# SLICE_4_1.md

## BeatSync Studio — Slice 4.1: Upload + Analysis Orchestration (Locked)

**Status:** FROZEN — DO NOT MODIFY

---

### Guarantees
- Canonical schema loaded from beatsync-core/schema/v0_1.json
- Output JSON is validated exactly, with no mutation or additions
- analysis_version and schema_version are preserved from BeatSync Core
- Only .wav, .mp3, .mid files accepted; all others rejected
- Missing or empty file → 400 Bad Request
- Unsupported extension → 400 Bad Request
- Output written to beatsync.tmp.json, renamed to beatsync.json only after validation
- BeatSync CLI invoked once, deterministically, with hard timeout
- Timeout or crash → 500, no residue or partial files
- Deterministic hash: SHA256(file bytes + analysis_version + schema_version)
- Same input always yields same hash and output
- Output stored at /storage/<analysis_hash>/beatsync.json
- No partial files survive any failure path
- Response contains only required fields: analysis_id, analysis_hash, schema_version, analysis_version, duration_sec, bpm, confidence, download_url
- Forbidden fields (_debug, _mutation, _internal) are fully removed
- download_url is present as a string (stubbed)

---

### Invariants
- No UI, auth, caching, logging, or background jobs
- No schema mutation, no field inference, no output drift
- No retries, no clever abstractions, no extra endpoints
- No refactoring or extension permitted after freeze

---

### Non-Goals
- No timeline visualization (see Slice 4.2)
- No storyboard or export logic
- No user authentication or project management
- No caching, previews, or derivative outputs
- No modification of BeatSync Core behavior

---

### Definition of Done
- All contract, determinism, and failure hygiene tests pass (see tests/test_api_analysis.py)
- Web output matches CLI output exactly
- Failures leave no residue
- Determinism holds across all runs
- This adapter can be deleted without breaking BeatSync Core

---

**This slice is now a locked contract. All downstream work must treat it as an oracle.**
