
import subprocess
import os
import sys

def test_missing_file(tmp_path):
	out_json = tmp_path / "out.json"
	python_exe = sys.executable
	cli_path = os.path.join(os.path.dirname(__file__), "..", "src", "beatsync_core", "cli.py")
	result = subprocess.run([
		python_exe, cli_path, "analyze", "not_a_real_file.wav", "--out", str(out_json)
	], capture_output=True, text=True)
	assert result.returncode != 0
	assert not out_json.exists()

def test_unsupported_extension(tmp_path):
	dummy = tmp_path / "file.txt"
	dummy.write_text("not audio")
	out_json = tmp_path / "out.json"
	python_exe = sys.executable
	cli_path = os.path.join(os.path.dirname(__file__), "..", "src", "beatsync_core", "cli.py")
	result = subprocess.run([
		python_exe, cli_path, "analyze", str(dummy), "--out", str(out_json)
	], capture_output=True, text=True)
	assert result.returncode != 0
	assert not out_json.exists()

# Short file test is a placeholder (would require a <2s audio fixture)
