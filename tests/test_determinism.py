import os
import json
import tempfile
import pytest
from src.cli import main as cli_main

def test_determinism(monkeypatch):
    midi_path = os.path.join(os.path.dirname(__file__), "dummy.mid")
    with open(midi_path, "wb") as f:
        f.write(b"MThd\x00\x00\x00\x06\x00\x01\x00\x01\x00\x60MTrk\x00\x00\x00\x04\x00\xFF\x2F\x00")
    out1 = tempfile.mktemp(suffix=".json")
    out2 = tempfile.mktemp(suffix=".json")
    args1 = ["analyze", midi_path, "--out", out1]
    args2 = ["analyze", midi_path, "--out", out2]
    monkeypatch.setattr("sys.argv", ["beatsync"] + args1)
    try:
        cli_main()
    except SystemExit:
        pass
    monkeypatch.setattr("sys.argv", ["beatsync"] + args2)
    try:
        cli_main()
    except SystemExit:
        pass
    with open(out1) as f1, open(out2) as f2:
        d1 = json.load(f1)
        d2 = json.load(f2)
    assert d1 == d2
    os.remove(midi_path)
    os.remove(out1)
    os.remove(out2)
