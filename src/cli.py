import argparse
import sys
import os
import tempfile
import json
from .midi_processor import analyze_midi

ANALYSIS_VERSION = "0.1.0"


def main():
    parser = argparse.ArgumentParser(description="BeatSync Core Analyzer")
    parser.add_argument("analyze", help="Analyze an audio or MIDI file", nargs='?')
    parser.add_argument("input_file", help="Input .wav, .mp3, or .mid file")
    parser.add_argument("--out", required=True, help="Output JSON file path")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    args = parser.parse_args()

    if not os.path.isfile(args.input_file):
        print(f"Error: Input file '{args.input_file}' not found.", file=sys.stderr)
        sys.exit(1)

    ext = os.path.splitext(args.input_file)[1].lower()
    try:
        if ext == ".mid":
            result = analyze_midi(args.input_file, ANALYSIS_VERSION)
        else:
            print("Error: Only MIDI (.mid) analysis is implemented in this stub.", file=sys.stderr)
            sys.exit(2)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(3)

    # Write to temp file first
    with tempfile.NamedTemporaryFile("w", delete=False, dir=os.path.dirname(args.out)) as tmp:
        json.dump(result, tmp, indent=2 if args.pretty else None)
        tempname = tmp.name

    os.replace(tempname, args.out)
    print(f"Analysis complete. Output written to {args.out}")
    sys.exit(0)

if __name__ == "__main__":
    main()
