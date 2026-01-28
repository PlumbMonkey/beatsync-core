import shutil
from pathlib import Path

# Golden regression generator for BeatSync MIDI
# Copies current CLI outputs as golden files for regression protection

def copy_to_golden(src_dir, golden_dir, midi_files):
    golden_dir.mkdir(parents=True, exist_ok=True)
    for midi_file in midi_files:
        midi_path = src_dir / midi_file
        report_path = src_dir / "report.json"
        if midi_path.exists():
            shutil.copy2(midi_path, golden_dir / midi_file)
        if report_path.exists():
            shutil.copy2(report_path, golden_dir / f"{midi_file}.report.json")

if __name__ == "__main__":
    # Example usage: run CLI, then copy outputs to golden
    out_dir = Path("beatsync-midi/tests/tmp_golden_out")
    golden_dir = Path("beatsync-midi/fixtures/golden")
    midi_files = ["valid1.mid", "valid2.mid"]
    copy_to_golden(out_dir, golden_dir, midi_files)
