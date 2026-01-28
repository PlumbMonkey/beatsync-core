import argparse
import sys
import os
import json
import tempfile
from beatsync_core.core import audio, midi, tempo, key, structure, energy
from beatsync_core.utils import io, validate

def main():
    parser = argparse.ArgumentParser(prog="beatsync", description="BeatSync Core CLI")
    subparsers = parser.add_subparsers(dest="command")

    analyze_parser = subparsers.add_parser("analyze", help="Analyze an audio or MIDI file")
    analyze_parser.add_argument("input_file", help="Input audio or MIDI file")
    analyze_parser.add_argument("--out", required=True, help="Output JSON file")
    analyze_parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")

    args = parser.parse_args()

    if args.command == "analyze":
        try:
            result = analyze_file(args.input_file)
            validate.validate_contract(result)
            write_json_atomic(result, args.out, pretty=args.pretty)
            print(f"Analysis complete: {args.out}")
            sys.exit(0)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)

def analyze_file(input_file):
    # Placeholder: choose analysis based on file type
    ext = os.path.splitext(input_file)[1].lower()
    if ext in [".wav", ".mp3", ".flac"]:
        return audio.analyze(input_file)
    elif ext in [".mid", ".midi"]:
        return midi.analyze(input_file)
    else:
        raise ValueError("Unsupported file extension")

def write_json_atomic(data, out_path, pretty=False):
    dir_name = os.path.dirname(out_path)
    os.makedirs(dir_name, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", dir=dir_name, delete=False, encoding="utf-8") as tf:
        json.dump(data, tf, indent=2 if pretty else None)
        tempname = tf.name
    os.replace(tempname, out_path)

if __name__ == "__main__":
    main()
