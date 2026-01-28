import subprocess
import os
import sys
import json
import numpy as np
from beatsync_core.utils import validate
from tests.tolerances import BPM_TOLERANCE, BEAT_TIMESTAMP_TOLERANCE, BAR_TIMESTAMP_TOLERANCE, PEAKS_TOLERANCE, ENERGY_MAE_TOLERANCE
from pathlib import Path

def assert_fixture_exists(path):
	if not path.exists() or path.stat().st_size == 0:
		raise AssertionError(f"Fixture {path} is missing/empty. Generate via scripts/make_midi_basic_100.py.")

def compare_with_tolerance(a, b):
	assert abs(a["tempo"]["bpm"] - b["tempo"]["bpm"]) <= BPM_TOLERANCE
	for x, y in zip(a["rhythm"]["beats"], b["rhythm"]["beats"]):
		assert abs(x - y) <= BEAT_TIMESTAMP_TOLERANCE
	for x, y in zip(a["rhythm"]["bars"], b["rhythm"]["bars"]):
		assert abs(x - y) <= BAR_TIMESTAMP_TOLERANCE
	for x, y in zip(a["energy"]["peaks"], b["energy"]["peaks"]):
		assert abs(x - y) <= PEAKS_TOLERANCE
	mae = sum(abs(x - y) for x, y in zip(a["energy"]["curve"], b["energy"]["curve"])) / max(1, len(a["energy"]["curve"]))
	assert mae <= ENERGY_MAE_TOLERANCE

def test_golden_audio(tmp_path):
	repo = Path(__file__).resolve().parents[1]
	fixture = repo / "fixtures" / "audio" / "click_120.wav"
	expected = repo / "expected" / "click_120.beatsync.json"
	out_json = tmp_path / "out.json"
	assert_fixture_exists(fixture)
	assert_fixture_exists(expected)
	python_exe = sys.executable
	cli_path = repo / "src" / "beatsync_core" / "cli.py"
	result = subprocess.run([
		python_exe, str(cli_path), "analyze", str(fixture), "--out", str(out_json)
	], capture_output=True, text=True)
	assert result.returncode == 0, f"CLI failed: {result.stderr}"
	with open(out_json, "r", encoding="utf-8") as f:
		actual = json.load(f)
	with open(expected, "r", encoding="utf-8") as f:
		golden = json.load(f)
	compare_with_tolerance(actual, golden)

def test_golden_midi(tmp_path):
	repo = Path(__file__).resolve().parents[1]
	fixture = repo / "fixtures" / "midi" / "midi_basic_100.mid"
	expected = repo / "expected" / "midi_basic_100.beatsync.json"
	out_json = tmp_path / "out.json"
	assert_fixture_exists(fixture)
	assert_fixture_exists(expected)
	python_exe = sys.executable
	cli_path = repo / "src" / "beatsync_core" / "cli.py"
	result = subprocess.run([
		python_exe, str(cli_path), "analyze", str(fixture), "--out", str(out_json)
	], capture_output=True, text=True)
	assert result.returncode == 0, f"CLI failed: {result.stderr}"
	with open(out_json, "r", encoding="utf-8") as f:
		actual = json.load(f)
	with open(expected, "r", encoding="utf-8") as f:
		golden = json.load(f)
	compare_with_tolerance(actual, golden)
