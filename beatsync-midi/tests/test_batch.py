import subprocess
import sys
import json
from pathlib import Path

def test_batch_processing(tmp_path):
    repo = Path(__file__).resolve().parents[1]
    batch_dir = repo / "fixtures" / "batch"
    out_dir = tmp_path / "out"
    python_exe = sys.executable
    cli_path = repo / "src" / "beatsync_midi" / "cli.py"
    result = subprocess.run([
        python_exe, str(cli_path), "process", str(batch_dir), "--out", str(out_dir)
    ], capture_output=True, text=True)
    assert result.returncode == 0, f"CLI failed: {result.stderr}"
    # Check output MIDI files
    midi1 = out_dir / "valid1.mid"
    midi2 = out_dir / "valid2.mid"
    assert midi1.exists() and midi1.stat().st_size > 0, "valid1.mid missing or empty"
    assert midi2.exists() and midi2.stat().st_size > 0, "valid2.mid missing or empty"
    # Check report
    report = out_dir / "report.json"
    assert report.exists() and report.stat().st_size > 0, "Report missing or empty"
    with open(report, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "files" in data and "skipped" in data
    skipped_files = {s["file"]: s["reason"] for s in data["skipped"]}
    assert "invalid.mid" in skipped_files and "missing or empty" in skipped_files["invalid.mid"]
    assert "not_a_midi.txt" in skipped_files and "not a MIDI file" in skipped_files["not_a_midi.txt"]
