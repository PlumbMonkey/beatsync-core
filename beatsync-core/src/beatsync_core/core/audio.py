import numpy as np
import gc
import librosa
from beatsync_core.core import tempo, energy, key, structure

FIXED_SR = 22050
MAX_DURATION_SEC = 60  # Free tier memory limit: 512MB
ANALYSIS_VERSION = "0.1"

def analyze(input_file):
    # Load audio: mono, 22050 Hz, max 60 seconds for memory efficiency
    try:
        y, sr = librosa.load(input_file, sr=FIXED_SR, mono=True, duration=MAX_DURATION_SEC)
    except Exception as e:
        raise ValueError(f"Failed to load audio file: {str(e)}")
    
    duration_sec = len(y) / sr
    
    # Tempo detection
    try:
        tempo_out = tempo.analyze(y, sr)
    except Exception as e:
        raise ValueError(f"Tempo analysis failed: {str(e)}")
    
    # Energy analysis
    try:
        energy_out = energy.analyze(y, sr)
    except Exception as e:
        raise ValueError(f"Energy analysis failed: {str(e)}")
    
    # Key detection
    try:
        key_out = key.analyze(y, sr)
    except Exception as e:
        raise ValueError(f"Key analysis failed: {str(e)}")
    
    # Structure analysis
    try:
        structure_out = structure.analyze(y, sr)
    except Exception as e:
        raise ValueError(f"Structure analysis failed: {str(e)}")
    
    # Free memory: delete raw audio after all analysis is complete
    del y
    gc.collect()
    
    # Rhythm: simple beat/bar grid based on detected BPM
    beats = [float(x) for x in np.arange(0, duration_sec, 60.0 / tempo_out["bpm"]).tolist()]
    bars = [float(x) for x in np.arange(0, duration_sec, 4 * 60.0 / tempo_out["bpm"]).tolist()]
    
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
