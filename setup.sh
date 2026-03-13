#!/usr/bin/env bash
# BeatSync Monorepo Build Script
# Run by Render during the build phase.
# Installs all local packages in dependency order so FastAPI can import them.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "=== BeatSync Build: Installing monorepo packages ==="
echo "Repo root: $REPO_ROOT"

pip install --upgrade pip

# Pin numpy first so librosa/scipy wheels use the correct ABI.
# numpy 2.4.3 is verified compatible with scipy 1.17.1 on Python 3.10.
echo "-> Pinning numpy 2.4.3..."
pip install "numpy==2.4.3"

# Install beatsync-core (-e = editable, registers it in site-packages
# so downstream packages resolve the beatsync_core>=0.1.0 dep locally).
echo "-> Installing beatsync-core..."
pip install -e "$REPO_ROOT/beatsync-core"

# Install beatsync-midi (depends on mido, numpy already satisfied above).
echo "-> Installing beatsync-midi..."
pip install -e "$REPO_ROOT/beatsync-midi"

# Install beatsync-studio. Its pyproject.toml lists beatsync_core>=0.1.0 as a
# dependency; pip finds it already installed above and does NOT go to PyPI.
echo "-> Installing beatsync-studio..."
pip install -e "$REPO_ROOT/beatsync-studio"

# Ensure uvicorn standard extras and multipart are present regardless of
# which pyproject.toml version constraint wins.
pip install "uvicorn[standard]>=0.27.0" "python-multipart>=0.0.9"

# --- Import smoke-test ---
# If any of these fail the build is aborted before Render ever tries to start
# the server, giving a clear error in the build log instead of a silent timeout.
echo "-> Verifying imports..."
python - <<'PYEOF'
import sys

try:
    from beatsync_core.core import audio, key, structure
    print("  [OK] beatsync_core (audio, key, structure)")
except Exception as e:
    print(f"  [FAIL] beatsync_core: {e}", file=sys.stderr)
    sys.exit(1)

try:
    from beatsync_midi import key_detect
    print("  [OK] beatsync_midi")
except Exception as e:
    print(f"  [FAIL] beatsync_midi: {e}", file=sys.stderr)
    sys.exit(1)

try:
    from beatsync_studio.main import app
    print("  [OK] beatsync_studio — FastAPI app loaded")
except Exception as e:
    print(f"  [FAIL] beatsync_studio: {e}", file=sys.stderr)
    sys.exit(1)

import numpy as np
import scipy
print(f"  [OK] numpy {np.__version__}, scipy {scipy.__version__}")
PYEOF

echo "=== Build complete ==="
