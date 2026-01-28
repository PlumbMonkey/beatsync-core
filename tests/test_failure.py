import os
import tempfile
import pytest
from src.cli import main as cli_main

def test_failure_modes(monkeypatch):
    # Corrupted file
    bad_path = os.path.join(os.path.dirname(__file__), "bad.mid")
    with open(bad_path, "wb") as f:
        f.write(b"not a midi file")
    out_path = tempfile.mktemp(suffix=".json")
    args = ["analyze", bad_path, "--out", out_path]
    monkeypatch.setattr("sys.argv", ["beatsync"] + args)
    with pytest.raises(SystemExit) as e:
        cli_main()
    assert e.value.code != 0
    assert not os.path.exists(out_path)
    os.remove(bad_path)
