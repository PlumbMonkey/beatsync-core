import mido
import numpy as np
from beatsync_core.core import tempo, energy, key, structure

ANALYSIS_VERSION = "0.1"

def analyze(input_file):
    mid = mido.MidiFile(input_file)
    duration_sec = mid.length
    # Estimate tempo from MIDI meta messages
    bpm = 120.0
    for track in mid.tracks:
        for msg in track:
            if msg.type == 'set_tempo':
                bpm = mido.tempo2bpm(msg.tempo)
                break
    tempo_out = tempo.analyze_midi(bpm)
    # Energy: use note-on density as a proxy
    note_ons = [msg.time for track in mid.tracks for msg in track if msg.type == 'note_on']
    if note_ons:
        times = np.cumsum(note_ons)
        curve, _ = np.histogram(times, bins=int(duration_sec))
        curve = curve / (curve.max() if curve.max() > 0 else 1)
        peaks = np.where(curve > 0.8)[0]
        energy_out = {"curve": curve.tolist(), "peaks": peaks.tolist()}
    else:
        energy_out = {"curve": [], "peaks": []}
    key_out = key.analyze_midi(mid)
    structure_out = structure.analyze_midi(mid)
    # Rhythm: simple beat/bar grid
    beats = np.arange(0, duration_sec, 60.0 / tempo_out["bpm"]).tolist()
    bars = np.arange(0, duration_sec, 4 * 60.0 / tempo_out["bpm"]).tolist()
    return {
        "metadata": {
            "source_file": input_file,
            "duration_sec": float(np.round(duration_sec, 3)),
            "analysis_version": ANALYSIS_VERSION
        },
        "tempo": tempo_out,
        "key": key_out,
        "rhythm": {"beats": beats, "bars": bars},
        "structure": structure_out,
        "energy": energy_out
    }
