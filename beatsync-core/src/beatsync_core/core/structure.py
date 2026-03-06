
"""Music structure segmentation using fast onset peak detection."""
import numpy as np
import librosa
from scipy.signal import find_peaks


def analyze(y: np.ndarray, sr: int) -> list:
    """
    Detect section boundaries in audio using fast onset peak detection.

    Uses onset strength peaks to identify regions of significant spectral change.
    Avoids expensive recurrence matrix and agglomerative clustering for fast performance on free tier.

    Args:
        y: Audio time series as numpy array.
        sr: Sampling rate of the audio.

    Returns:
        List of sections, each a dict with:
            - "label": Section name (e.g., "section_1")
            - "start": Start time in seconds (float)
            - "end": End time in seconds (float)

        If fewer than 2 boundaries detected, returns a single section
        covering the full track duration.
    """
    try:
        # Handle edge cases
        if len(y) == 0:
            return []

        # Compute onset strength (spectral novelty) - fast
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        
        # Fast: detect peaks in onset strength directly
        # Avoid O(N²) recurrence matrix computation
        if len(onset_env) > 0:
            # Normalize onset strength
            if onset_env.max() > 0:
                onset_normalized = onset_env / onset_env.max()
            else:
                onset_normalized = onset_env
            
            # Find peaks with reasonable spacing (minimum 4 seconds between boundaries)
            min_distance = int(4.0 * sr / 512)  # 512 is librosa's default hop_length
            peaks, _ = find_peaks(onset_normalized, height=0.4, distance=min_distance)
        else:
            peaks = np.array([])

        # Convert frame indices to time
        boundary_frames = np.concatenate([[0], peaks, [len(onset_env) - 1]])
        boundary_times = librosa.frames_to_time(boundary_frames, sr=sr)
        boundary_times = np.unique(boundary_times)

        duration = librosa.get_duration(y=y, sr=sr)
        
        # Ensure boundaries span the full track
        boundary_times = np.unique(np.concatenate([[0.0], boundary_times, [duration]]))

        # Filter out boundaries that are too close (minimum section length: 4 seconds)
        min_section_length = 4.0
        filtered_boundaries = [boundary_times[0]]
        for t in boundary_times[1:]:
            if t - filtered_boundaries[-1] >= min_section_length:
                filtered_boundaries.append(t)
        # Always include the end
        if filtered_boundaries[-1] < duration:
            filtered_boundaries.append(duration)

        # If fewer than 2 boundaries remain after filtering, return single section
        if len(filtered_boundaries) < 2:
            return [{
                "label": "section_1",
                "start": float(0.0),
                "end": float(duration),
                "confidence": float(0.5)
            }]

        # Create section list with confidence based on onset strength in each section
        sections = []
        for i in range(len(filtered_boundaries) - 1):
            start = float(filtered_boundaries[i])
            end = float(filtered_boundaries[i + 1])
            
            # Compute confidence: mean onset strength in this section
            # Higher onset activity = higher confidence in section boundary
            start_frame = int(librosa.time_to_frames(start, sr=sr))
            end_frame = int(librosa.time_to_frames(end, sr=sr))
            section_onset = onset_env[start_frame:end_frame]
            
            if len(section_onset) > 0 and onset_env.max() > 0:
                confidence = float(np.mean(section_onset) / onset_env.max())
                confidence = float(np.clip(confidence, 0.0, 1.0))
            else:
                confidence = float(0.5)
            
            sections.append({
                "label": f"section_{i + 1}",
                "start": float(start),
                "end": float(end),
                "confidence": confidence
            })

        return sections

    except Exception:
        # Fallback: return empty list on any error
        return []


def analyze_midi(mid):
    """Placeholder for MIDI structure analysis (not implemented)."""
    return []
