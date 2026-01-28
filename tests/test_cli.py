import os
import json
import tempfile
import pytest
from src.cli import main as cli_main

def test_cli_midi(monkeypatch):
    # Prepare dummy MIDI file
    midi_path = os.path.join(os.path.dirname(__file__), "dummy.mid")
    with open(midi_path, "wb") as f:
        f.write(b"MThd\x00\x00\x00\x06\x00\x01\x00\x01\x00\x60MTrk\x00\x00\x00\x04\x00\xFF\x2F\x00")
    out_path = tempfile.mktemp(suffix=".json")
    args = ["analyze", midi_path, "--out", out_path]
    monkeypatch.setattr("sys.argv", ["beatsync"] + args)
    try:
        cli_main()
    except SystemExit as e:
        assert e.code == 0
    with open(out_path) as f:
        data = json.load(f)
    assert "metadata" in data
    assert data["metadata"]["source_file"].endswith("dummy.mid")
    assert "tempo" in data
    assert "key" in data
    assert "rhythm" in data
    assert "structure" in data
    assert "energy" in data
    os.remove(midi_path)
    os.remove(out_path)
