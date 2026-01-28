
import argparse
import sys
import os
import shutil
import json
from pathlib import Path
import mido



def main():
    parser = argparse.ArgumentParser(prog="beatsync-midi", description="BeatSync MIDI CLI")
    subparsers = parser.add_subparsers(dest="command")

    process_parser = subparsers.add_parser("process", help="Process a MIDI file or folder")
    process_parser.add_argument("input_path", help="Input MIDI file or folder")
    process_parser.add_argument("--out", required=True, help="Output folder")
    process_parser.add_argument("--strict", action="store_true", help="Halt on first failure")

    process_parser.add_argument("--target-bpm", type=float, help="Retarget MIDI to this BPM")
    process_parser.add_argument("--target-key", type=str, help="Transpose MIDI to this key (e.g., Am, C, F#)")
    process_parser.add_argument("--confidence-threshold", type=float, default=0.0, help="Skip files with key confidence below this value")

    parser.add_argument('--version', action='version', version='BeatSync MIDI 0.1.0')
    args = parser.parse_args()

    if args.command == "process":
        try:
            input_path = Path(args.input_path)
            if input_path.is_dir():
                process_batch(
                    input_path,
                    args.out,
                    strict=args.strict,
                    target_bpm=args.target_bpm,
                    target_key=args.target_key,
                    confidence_threshold=args.confidence_threshold
                )
            else:
                process_single(
                    input_path,
                    args.out,
                    target_bpm=args.target_bpm,
                    target_key=args.target_key,
                    confidence_threshold=args.confidence_threshold
                )
            sys.exit(0)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(0)

def process_batch(input_dir, out_folder, strict=False, target_bpm=None, target_key=None, confidence_threshold=0.0):
    input_dir = Path(input_dir)
    out_dir = Path(out_folder)
    out_dir.mkdir(parents=True, exist_ok=True)
    report = {"files": [], "skipped": []}
    any_skipped = False
    for f in sorted(input_dir.iterdir()):
        if f.suffix.lower() != ".mid":
            report["skipped"].append({"file": f.name, "reason": "not a MIDI file"})
            continue
        if not f.is_file() or f.stat().st_size == 0:
            report["skipped"].append({"file": f.name, "reason": "missing or empty"})
            if strict:
                break
            continue
        try:
            # Wrap process_single to catch sys.exit(2) for low-confidence skip
            try:
                process_single(f, out_dir, target_bpm=target_bpm, target_key=target_key, confidence_threshold=confidence_threshold)
                # If no sys.exit, status is processed
                report["files"].append(f.name)
            except SystemExit as se:
                if se.code == 2:
                    any_skipped = True
                    report["skipped"].append({"file": f.name, "reason": "low confidence"})
                else:
                    raise
        except Exception as e:
            report["skipped"].append({"file": f.name, "reason": str(e)})
            if strict:
                break
    with open(out_dir / "report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    if any_skipped:
        sys.exit(2)


def transpose_midi(mid: mido.MidiFile, semitone_shift: int) -> mido.MidiFile:
    for track in mid.tracks:
        for msg in track:
            if msg.type in ("note_on", "note_off") and hasattr(msg, "note"):
                msg.note = min(127, max(0, msg.note + semitone_shift))
    return mid

def process_single(input_midi, out_folder, target_bpm=None, target_key=None, confidence_threshold=0.0):
    in_path = Path(input_midi)
    out_dir = Path(out_folder)
    out_dir.mkdir(parents=True, exist_ok=True)
    midi_out = out_dir / in_path.name
    # Load MIDI
    mid = mido.MidiFile(str(in_path))
    orig_tempo = None
    for track in mid.tracks:
        for msg in track:
            if msg.type == 'set_tempo':
                orig_tempo = msg.tempo
                break
        if orig_tempo:
            break
    actions = []
    # Retiming
    if target_bpm is not None and orig_tempo is not None:
        orig_bpm = mido.tempo2bpm(orig_tempo)
        scale = orig_bpm / target_bpm
        for track in mid.tracks:
            for msg in track:
                if hasattr(msg, 'time'):
                    msg.time = int(round(msg.time * scale))
        for track in mid.tracks:
            for i, msg in enumerate(track):
                if msg.type == 'set_tempo':
                    track[i] = mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(target_bpm), time=msg.time)
                    break
        actions.append(f"retimed to {target_bpm} BPM")
    # Key detection (placeholder: always C, confidence 1.0)
    detected_key = "C"
    key_confidence = 1.0
    semitone_shift = 0
    # Transposition
    if target_key is not None:
        key_map = {"C": 0, "G": 7, "F": 5, "D": 2, "A": 9, "E": 4, "B": 11, "Am": 9, "Em": 4, "Dm": 2}
        target_key_val = key_map.get(target_key, 0)
        detected_key_val = key_map.get(detected_key, 0)
        semitone_shift = (target_key_val - detected_key_val) % 12
        if key_confidence < confidence_threshold:
            # Write skip report and exit code 2
            report = {
                "input_filename": in_path.name,
                "detected_key": detected_key,
                "key_confidence": key_confidence,
                "target_key": target_key,
                "semitone_shift": semitone_shift,
                "status": "skipped",
                "reason": f"Key confidence {key_confidence} below threshold {confidence_threshold}"
            }
            with open(out_dir / "report.json", "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2)
            sys.exit(2)
        mid = transpose_midi(mid, semitone_shift)
        actions.append(f"transposed to {target_key}")
    # Save output MIDI
    mid.save(midi_out.as_posix())
    # Generate report.json
    tempo = None
    key = detected_key
    try:
        for track in mid.tracks:
            for msg in track:
                if msg.type == 'set_tempo':
                    tempo = round(mido.tempo2bpm(msg.tempo), 2)
                    break
            if tempo:
                break
    except Exception:
        tempo = None
    report = {
        "input_filename": in_path.name,
        "detected_tempo": tempo,
        "detected_key": key,
        "key_confidence": key_confidence,
        "target_key": target_key,
        "semitone_shift": semitone_shift,
        "actions": actions,
        "status": "processed"
    }
    with open(out_dir / "report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

if __name__ == "__main__":
    main()
