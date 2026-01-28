import subprocess
import sys
import json
from pathlib import Path

def test_cli_smoke(tmp_path):
    repo = Path(__file__).resolve().parents[1]
    fixture = repo / "fixtures" / "midi_basic_100.mid"
    out_dir = tmp_path / "out"
    python_exe = sys.executable
    cli_path = repo / "src" / "beatsync_midi" / "cli.py"
    result = subprocess.run([
        python_exe, str(cli_path), "process", str(fixture), "--out", str(out_dir)
    ], capture_output=True, text=True)
    assert result.returncode == 0, f"CLI failed: {result.stderr}"
    midi_out = out_dir / fixture.name
    report = out_dir / "report.json"
    assert midi_out.exists() and midi_out.stat().st_size > 0, "Output MIDI missing or empty"
    assert report.exists() and report.stat().st_size > 0, "Report missing or empty"
    with open(report, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "input_filename" in data and "detected_tempo" in data and "detected_key" in data and "actions" in data
