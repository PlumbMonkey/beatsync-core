import subprocess
import sys
from pathlib import Path
import pytest
import mido
import json

def normalize_midi_events(midi_path):
    mid = mido.MidiFile(str(midi_path))
    events = []
    for track in mid.tracks:
        for msg in track:
            if msg.type in ("note_on", "note_off"):
                events.append({
                    "type": msg.type,
                    "note": msg.note,
                    "velocity": getattr(msg, "velocity", 0),
                    "time": msg.time
                })
    return events

def normalize_json(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return json.dumps(data, sort_keys=True, indent=2)

@pytest.mark.parametrize("fixture_name", ["valid1.mid", "valid2.mid"])
def test_golden_regression(tmp_path, fixture_name):
    repo = Path(__file__).resolve().parents[1]
    fixture_dir = repo / "fixtures" / "batch"
    golden_dir = repo / "fixtures" / "golden"
    out_dir = tmp_path / "out"
    out_dir.mkdir(exist_ok=True)

    fixture = fixture_dir / fixture_name
    golden_midi = golden_dir / fixture_name
    golden_report = golden_dir / f"{fixture_name}.report.json"

    # Sanity checks
    assert fixture.exists() and fixture.stat().st_size > 0, f"Missing or empty fixture: {fixture}"
    assert golden_midi.exists(), f"Missing golden MIDI: {golden_midi}. Run scripts/generate_goldens.py to create it."
    assert golden_report.exists(), f"Missing golden report: {golden_report}. Run scripts/generate_goldens.py to create it."

    cli_path = repo / "src" / "beatsync_midi" / "cli.py"
    python_exe = sys.executable

    result = subprocess.run([
        python_exe, str(cli_path), "process", str(fixture), "--out", str(out_dir),
        "--target-bpm", "120", "--target-key", "G", "--confidence-threshold", "0.0"
    ], capture_output=True, text=True)
    assert result.returncode == 0, f"CLI failed: {result.stderr}"

    midi_out = out_dir / fixture_name
    report_out = out_dir / "report.json"

    assert midi_out.exists(), f"Missing output MIDI: {midi_out}"
    assert report_out.exists(), f"Missing output report: {report_out}"

    # Compare normalized MIDI events
    midi_events = normalize_midi_events(midi_out)
    golden_events = normalize_midi_events(golden_midi)
    assert midi_events == golden_events, f"MIDI event list mismatch for {fixture_name}"

    # Compare sorted JSON reports
    norm_report = normalize_json(report_out)
    norm_golden_report = normalize_json(golden_report)
    assert norm_report == norm_golden_report, f"Report output mismatch for {fixture_name}"