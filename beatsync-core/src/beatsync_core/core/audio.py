import numpy as np
import soundfile as sf
from scipy.signal import find_peaks
from beatsync_core.core import tempo, energy, key, structure

FIXED_SR = 22050
ANALYSIS_VERSION = "0.1"

def analyze(input_file):
    # Load audio
    y, sr = sf.read(input_file)
    if y.ndim > 1:
        y = y.mean(axis=1)  # mono
    duration_sec = len(y) / sr
    # Resample if needed
    if sr != FIXED_SR:
        from scipy.signal import resample
        y = resample(y, int(FIXED_SR * duration_sec))
        sr = FIXED_SR
    # Tempo
    tempo_out = tempo.analyze(y, sr)
    # Energy
    energy_out = energy.analyze(y, sr)
    # Key (placeholder)
    key_out = key.analyze(y, sr)
    # Structure (placeholder)
    structure_out = structure.analyze(y, sr)
    # Rhythm (simple beat grid)
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
