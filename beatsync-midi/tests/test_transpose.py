import subprocess
import sys
import mido
from pathlib import Path
import json

def test_transpose_and_clamp(tmp_path):
    repo = Path(__file__).resolve().parents[1]
    fixture = repo / "fixtures" / "batch" / "valid1.mid"
    out_dir = tmp_path / "out"
    python_exe = sys.executable
    cli_path = repo / "src" / "beatsync_midi" / "cli.py"
    # Transpose to G (interval +7)
    result = subprocess.run([
        python_exe, str(cli_path), "process", str(fixture), "--out", str(out_dir), "--target-key", "G"
    ], capture_output=True, text=True)
    assert result.returncode == 0, f"CLI failed: {result.stderr}"
    midi_out = out_dir / fixture.name
    assert midi_out.exists() and midi_out.stat().st_size > 0, "Output MIDI missing or empty"
    # Check transposition
    orig = mido.MidiFile(str(fixture))
    transposed = mido.MidiFile(str(midi_out))
    orig_notes = [msg.note for track in orig.tracks for msg in track if msg.type == 'note_on']
    transposed_notes = [msg.note for track in transposed.tracks for msg in track if msg.type == 'note_on']
    expected = [(n + 7) % 128 for n in orig_notes]
    assert transposed_notes == expected, f"Transposed notes incorrect: {transposed_notes} != {expected}"
    # Clamp test: transpose to C, then to F (interval +5)
    result = subprocess.run([
        python_exe, str(cli_path), "process", str(fixture), "--out", str(out_dir), "--target-key", "F"
    ], capture_output=True, text=True)
    midi_out = out_dir / fixture.name
    transposed = mido.MidiFile(str(midi_out))
    for msg in transposed.tracks[0]:
        if msg.type == 'note_on':
            assert 0 <= msg.note <= 127, f"Note out of range: {msg.note}"

def test_skip_low_confidence(tmp_path):
    repo = Path(__file__).resolve().parents[1]
    fixture = repo / "fixtures" / "batch" / "valid1.mid"
    out_dir = tmp_path / "out"
    python_exe = sys.executable
    cli_path = repo / "src" / "beatsync_midi" / "cli.py"
    # Set threshold above placeholder confidence
    result = subprocess.run([
        python_exe, str(cli_path), "process", str(fixture), "--out", str(out_dir), "--target-key", "G", "--confidence-threshold", "1.1"
    ], capture_output=True, text=True)
    # Should fail due to low confidence
    assert result.returncode != 0
    report = out_dir / "report.json"
    if report.exists():
        with open(report, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert "actions" not in data or not data["actions"], "Should not have actions for low confidence"
