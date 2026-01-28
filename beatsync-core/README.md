# BeatSync Core

BeatSync Core is a headless music analysis engine that ingests audio or MIDI and outputs a deterministic structural representation of the track as a versioned JSON contract.

## Features
- Deterministic analysis of audio and MIDI
- Outputs tempo, beat/bar grids, key, sections, and energy curve
- JSON contract as single source of truth

## CLI Usage
```
beatsync analyze <input_file> --out <output_json> [--pretty]
```

## License
Apache-2.0
