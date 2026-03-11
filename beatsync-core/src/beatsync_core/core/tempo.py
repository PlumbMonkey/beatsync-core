
import numpy as np
import librosa

def analyze(y, sr):
	# Use librosa's beat tracker (onset-autocorrelation, O(N log N))
	tempo_arr, _ = librosa.beat.beat_track(y=y, sr=sr)
	# librosa >= 0.10 returns an array; take the first element
	if hasattr(tempo_arr, '__len__') and len(tempo_arr) > 0:
		bpm = float(tempo_arr[0])
	else:
		bpm = float(tempo_arr)
	bpm = float(np.round(bpm, 2))
	confidence = 0.9 if bpm > 0 else 0.0
	return {"bpm": bpm, "confidence": confidence}

def analyze_midi(bpm):
	return {"bpm": float(np.round(bpm, 2)), "confidence": float(1.0)}
