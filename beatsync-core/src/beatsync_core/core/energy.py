
import numpy as np
from scipy.signal import find_peaks

def analyze(y, sr):
	# Frame-wise RMS energy
	frame_size = int(0.05 * sr)  # 50ms
	hop = frame_size
	frames = [y[i:i+frame_size] for i in range(0, len(y)-frame_size+1, hop)]
	rms = np.array([np.sqrt(np.mean(f**2)) for f in frames])
	if rms.max() > 0:
		curve = (rms / rms.max()).tolist()
	else:
		curve = rms.tolist()
	peaks, _ = find_peaks(rms, height=0.8*rms.max())
	peak_times = (np.array(peaks) * hop / sr).tolist()
	return {"curve": curve, "peaks": peak_times}
