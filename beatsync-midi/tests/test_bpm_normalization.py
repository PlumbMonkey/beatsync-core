import subprocess
import sys
import mido
from pathlib import Path
import json

def test_bpm_normalization_and_integrity(tmp_path):
    repo = Path(__file__).resolve().parents[1]
    fixture = repo / "fixtures" / "batch" / "valid1.mid"
    out_dir = tmp_path / "out"
    python_exe = sys.executable
    cli_path = repo / "src" / "beatsync_midi" / "cli.py"
    target_bpm = 120
    result = subprocess.run([
        python_exe, str(cli_path), "process", str(fixture), "--out", str(out_dir), "--target-bpm", str(target_bpm)
    ], capture_output=True, text=True)
    assert result.returncode == 0, f"CLI failed: {result.stderr}"
    midi_out = out_dir / fixture.name
    assert midi_out.exists() and midi_out.stat().st_size > 0, "Output MIDI missing or empty"
    # Check MIDI integrity
    orig = mido.MidiFile(str(fixture))
    retimed = mido.MidiFile(str(midi_out))
    orig_notes = [(msg.note, msg.velocity) for track in orig.tracks for msg in track if msg.type == 'note_on']
    retimed_notes = [(msg.note, msg.velocity) for track in retimed.tracks for msg in track if msg.type == 'note_on']
    assert orig_notes == retimed_notes, "Note pitch/velocity changed during retiming"
    assert sum(1 for track in orig.tracks for msg in track if msg.type == 'note_on') == sum(1 for track in retimed.tracks for msg in track if msg.type == 'note_on'), "Note count changed during retiming"
    # Check tempo meta
    found_tempo = None
    for track in retimed.tracks:
        for msg in track:
            if msg.type == 'set_tempo':
                found_tempo = round(mido.tempo2bpm(msg.tempo))
                break
        if found_tempo:
            break
    assert found_tempo == target_bpm, f"Tempo meta not updated: {found_tempo} != {target_bpm}"
    # Check determinism
    result2 = subprocess.run([
        python_exe, str(cli_path), "process", str(fixture), "--out", str(out_dir), "--target-bpm", str(target_bpm)
    ], capture_output=True, text=True)
    midi_out2 = out_dir / fixture.name
    retimed2 = mido.MidiFile(str(midi_out2))
    retimed_notes2 = [(msg.note, msg.velocity) for track in retimed2.tracks for msg in track if msg.type == 'note_on']
    assert retimed_notes == retimed_notes2, "Retiming is not deterministic"
