
"""Music structure segmentation using novelty-based boundary detection."""
import numpy as np
import librosa


def analyze(y: np.ndarray, sr: int) -> list:
    """
    Detect section boundaries in audio using spectral novelty and segmentation.

    Uses onset strength to identify regions of significant spectral change,
    then applies agglomerative clustering to identify section boundaries.

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

        # Compute onset strength (spectral novelty)
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        times = librosa.frames_to_time(np.arange(len(onset_env)), sr=sr)

        # Compute recurrence matrix to find self-similar structure
        recurrence = librosa.segment.recurrence_matrix(
            onset_env,
            mode='affinity',
            sym=True
        )

        # Apply agglomerative clustering to find boundaries
        boundaries = librosa.segment.agglomerative(recurrence, k=max(2, len(onset_env) // 10))

        # Convert frame indices to time
        boundary_times = librosa.frames_to_time(boundaries, sr=sr)
        boundary_times = np.sort(boundary_times)

        # Ensure boundaries span the full track
        duration = librosa.get_duration(y=y, sr=sr)
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
                "start": 0.0,
                "end": duration
            }]

        # Create section list
        sections = []
        for i in range(len(filtered_boundaries) - 1):
            start = float(filtered_boundaries[i])
            end = float(filtered_boundaries[i + 1])
            sections.append({
                "label": f"section_{i + 1}",
                "start": start,
                "end": end
            })

        return sections

    except Exception:
        # Fallback: return empty list on any error
        return []


def analyze_midi(mid):
    """Placeholder for MIDI structure analysis (not implemented)."""
    return []
