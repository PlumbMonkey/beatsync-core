import subprocess
import os
import sys
import json
from beatsync_core.utils import validate

def test_cli_smoke(tmp_path):
    fixture = os.path.join(os.path.dirname(__file__), "..", "fixtures", "audio", "click_120.wav")
    out_json = tmp_path / "out.json"
    python_exe = sys.executable
    cli_path = os.path.join(os.path.dirname(__file__), "..", "src", "beatsync_core", "cli.py")
    result = subprocess.run([
        python_exe, cli_path, "analyze", fixture, "--out", str(out_json)
    ], capture_output=True, text=True)
    assert result.returncode == 0, f"CLI failed: {result.stderr}"
    with open(out_json, "r", encoding="utf-8") as f:
        data = json.load(f)
    validate.validate_contract(data)
