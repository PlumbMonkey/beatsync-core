
import subprocess
import os
import sys
import json
from beatsync_core.utils import validate
from tests.tolerances import BPM_TOLERANCE, BEAT_TIMESTAMP_TOLERANCE, BAR_TIMESTAMP_TOLERANCE, PEAKS_TOLERANCE, ENERGY_MAE_TOLERANCE

def test_determinism_audio(tmp_path):
	fixture = os.path.join(os.path.dirname(__file__), "..", "fixtures", "audio", "click_120.wav")
	outputs = []
	python_exe = sys.executable
	cli_path = os.path.join(os.path.dirname(__file__), "..", "src", "beatsync_core", "cli.py")
	for i in range(3):
		out_json = tmp_path / f"out_{i}.json"
		result = subprocess.run([
			python_exe, cli_path, "analyze", fixture, "--out", str(out_json)
		], capture_output=True, text=True)
		assert result.returncode == 0, f"CLI failed: {result.stderr}"
		with open(out_json, "r", encoding="utf-8") as f:
			outputs.append(json.load(f))
	# Compare outputs within tolerances
	for a, b in zip(outputs, outputs[1:]):
		assert abs(a["tempo"]["bpm"] - b["tempo"]["bpm"]) <= BPM_TOLERANCE
		for x, y in zip(a["rhythm"]["beats"], b["rhythm"]["beats"]):
			assert abs(x - y) <= BEAT_TIMESTAMP_TOLERANCE
		for x, y in zip(a["rhythm"]["bars"], b["rhythm"]["bars"]):
			assert abs(x - y) <= BAR_TIMESTAMP_TOLERANCE
		for x, y in zip(a["energy"]["peaks"], b["energy"]["peaks"]):
			assert abs(x - y) <= PEAKS_TOLERANCE
		mae = sum(abs(x - y) for x, y in zip(a["energy"]["curve"], b["energy"]["curve"])) / max(1, len(a["energy"]["curve"]))
		assert mae <= ENERGY_MAE_TOLERANCE
