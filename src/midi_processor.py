import mido
import os

def analyze_midi(input_file, analysis_version):
    try:
        mid = mido.MidiFile(input_file)
        duration_sec = mid.length
    except OSError as e:
        raise RuntimeError(f"MIDI file error: {e}")
    # Dummy values for demonstration
    bpm = 120.0
    bpm_conf = 0.9
    key = "C major"
    key_conf = 0.7
    beats = [0.0, 0.5, 1.0]
    bars = [0.0, 2.0, 4.0]
    structure = [
        {"label": "intro", "start": 0.0, "end": 16.0, "confidence": 0.8}
    ]
    energy_curve = [0.1, 0.2, 0.3]
    energy_peaks = [32.0, 64.0]
    return {
        "metadata": {
            "source_file": os.path.basename(input_file),
            "duration_sec": duration_sec,
            "analysis_version": analysis_version
        },
        "tempo": {
            "bpm": bpm,
            "confidence": bpm_conf
        },
        "key": {
            "name": key,
            "confidence": key_conf
        },
        "rhythm": {
            "beats": beats,
            "bars": bars
        },
        "structure": structure,
        "energy": {
            "curve": energy_curve,
            "peaks": energy_peaks
        }
    }
