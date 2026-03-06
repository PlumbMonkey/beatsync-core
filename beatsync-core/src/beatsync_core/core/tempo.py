
import numpy as np

def analyze(y, sr):
	# Simple energy-based BPM estimate (deterministic, not robust)
	duration = len(y) / sr
	# Use autocorrelation to estimate tempo
	y = y - np.mean(y)
	corr = np.correlate(y, y, mode='full')
	corr = corr[len(corr)//2:]
	min_bpm = 60
	max_bpm = 180
	min_lag = int(sr * 60 / max_bpm)
	max_lag = int(sr * 60 / min_bpm)
	peak_lag = np.argmax(corr[min_lag:max_lag]) + min_lag
	bpm = 60 * sr / peak_lag if peak_lag > 0 else 120.0
	bpm = float(np.round(bpm, 2))
	return {"bpm": bpm, "confidence": 0.9}

def analyze_midi(bpm):
	return {"bpm": float(np.round(bpm, 2)), "confidence": float(1.0)}
