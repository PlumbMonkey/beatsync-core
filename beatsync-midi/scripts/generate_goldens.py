import subprocess
from pathlib import Path

# List of valid fixtures to use for golden generation
VALID_FIXTURES = [
    "valid1.mid",
    "valid2.mid"
]

REPO = Path(__file__).resolve().parents[1]
FIXTURE_DIR = REPO / "fixtures" / "batch"
GOLDEN_DIR = REPO / "fixtures" / "golden"
CLI_PATH = REPO / "src" / "beatsync_midi" / "cli.py"
PYTHON_EXE = REPO.parent / ".venv" / "Scripts" / "python.exe"

def main():
    GOLDEN_DIR.mkdir(parents=True, exist_ok=True)
    for midi_name in VALID_FIXTURES:
        midi_path = FIXTURE_DIR / midi_name
        if not midi_path.exists() or midi_path.stat().st_size == 0:
            print(f"Fixture missing or empty: {midi_path}")
            continue
        out_dir = GOLDEN_DIR
        cmd = [
            str(PYTHON_EXE), str(CLI_PATH), "process", str(midi_path),
            "--out", str(out_dir),
            "--target-bpm", "120",
            "--target-key", "G",
            "--confidence-threshold", "0.0"
        ]
        print(f"Generating golden for {midi_name}...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Failed to generate golden for {midi_name}: {result.stderr}")
        else:
            # Rename report.json to validX.mid.report.json
            report_path = out_dir / "report.json"
            target_report = out_dir / f"{midi_name}.report.json"
            if report_path.exists():
                report_path.replace(target_report)
            print(f"Golden generated for {midi_name}")

if __name__ == "__main__":
    main()
