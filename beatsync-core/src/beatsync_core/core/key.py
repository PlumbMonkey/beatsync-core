
"""Audio key detection using chromagram and Krumhansl-Schmuckler profiles."""
import numpy as np
from scipy.stats import pearsonr
import librosa


# Krumhansl-Schmuckler profiles for major and minor keys
# Profiles for all 12 chromatic pitches: C, C#, D, D#, E, F, F#, G, G#, A, A#, B
MAJOR_PROFILES = {
    "C": [0.15249, 0.02520, 0.11691, 0.13063, 0.05000, 0.02488, 0.10690, 0.15613, 0.08616, 0.03112, 0.08616, 0.04572],
    "C#": [0.04572, 0.15249, 0.02520, 0.11691, 0.13063, 0.05000, 0.02488, 0.10690, 0.15613, 0.08616, 0.03112, 0.08616],
    "D": [0.08616, 0.04572, 0.15249, 0.02520, 0.11691, 0.13063, 0.05000, 0.02488, 0.10690, 0.15613, 0.08616, 0.03112],
    "D#": [0.03112, 0.08616, 0.04572, 0.15249, 0.02520, 0.11691, 0.13063, 0.05000, 0.02488, 0.10690, 0.15613, 0.08616],
    "E": [0.08616, 0.03112, 0.08616, 0.04572, 0.15249, 0.02520, 0.11691, 0.13063, 0.05000, 0.02488, 0.10690, 0.15613],
    "F": [0.15613, 0.08616, 0.03112, 0.08616, 0.04572, 0.15249, 0.02520, 0.11691, 0.13063, 0.05000, 0.02488, 0.10690],
    "F#": [0.10690, 0.15613, 0.08616, 0.03112, 0.08616, 0.04572, 0.15249, 0.02520, 0.11691, 0.13063, 0.05000, 0.02488],
    "G": [0.02488, 0.10690, 0.15613, 0.08616, 0.03112, 0.08616, 0.04572, 0.15249, 0.02520, 0.11691, 0.13063, 0.05000],
    "G#": [0.05000, 0.02488, 0.10690, 0.15613, 0.08616, 0.03112, 0.08616, 0.04572, 0.15249, 0.02520, 0.11691, 0.13063],
    "A": [0.13063, 0.05000, 0.02488, 0.10690, 0.15613, 0.08616, 0.03112, 0.08616, 0.04572, 0.15249, 0.02520, 0.11691],
    "A#": [0.11691, 0.13063, 0.05000, 0.02488, 0.10690, 0.15613, 0.08616, 0.03112, 0.08616, 0.04572, 0.15249, 0.02520],
    "B": [0.02520, 0.11691, 0.13063, 0.05000, 0.02488, 0.10690, 0.15613, 0.08616, 0.03112, 0.08616, 0.04572, 0.15249],
}

MINOR_PROFILES = {
    "C": [0.17454, 0.00874, 0.11813, 0.13428, 0.00702, 0.14885, 0.06142, 0.16608, 0.04374, 0.14138, 0.04374, 0.06142],
    "C#": [0.06142, 0.17454, 0.00874, 0.11813, 0.13428, 0.00702, 0.14885, 0.06142, 0.16608, 0.04374, 0.14138, 0.04374],
    "D": [0.04374, 0.06142, 0.17454, 0.00874, 0.11813, 0.13428, 0.00702, 0.14885, 0.06142, 0.16608, 0.04374, 0.14138],
    "D#": [0.14138, 0.04374, 0.06142, 0.17454, 0.00874, 0.11813, 0.13428, 0.00702, 0.14885, 0.06142, 0.16608, 0.04374],
    "E": [0.04374, 0.14138, 0.04374, 0.06142, 0.17454, 0.00874, 0.11813, 0.13428, 0.00702, 0.14885, 0.06142, 0.16608],
    "F": [0.16608, 0.04374, 0.14138, 0.04374, 0.06142, 0.17454, 0.00874, 0.11813, 0.13428, 0.00702, 0.14885, 0.06142],
    "F#": [0.06142, 0.16608, 0.04374, 0.14138, 0.04374, 0.06142, 0.17454, 0.00874, 0.11813, 0.13428, 0.00702, 0.14885],
    "G": [0.14885, 0.06142, 0.16608, 0.04374, 0.14138, 0.04374, 0.06142, 0.17454, 0.00874, 0.11813, 0.13428, 0.00702],
    "G#": [0.00702, 0.14885, 0.06142, 0.16608, 0.04374, 0.14138, 0.04374, 0.06142, 0.17454, 0.00874, 0.11813, 0.13428],
    "A": [0.13428, 0.00702, 0.14885, 0.06142, 0.16608, 0.04374, 0.14138, 0.04374, 0.06142, 0.17454, 0.00874, 0.11813],
    "A#": [0.11813, 0.13428, 0.00702, 0.14885, 0.06142, 0.16608, 0.04374, 0.14138, 0.04374, 0.06142, 0.17454, 0.00874],
    "B": [0.00874, 0.11813, 0.13428, 0.00702, 0.14885, 0.06142, 0.16608, 0.04374, 0.14138, 0.04374, 0.06142, 0.17454],
}

PITCH_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def analyze(y: np.ndarray, sr: int) -> dict:
    """
    Detect the key of an audio signal using chromagram and Krumhansl-Schmuckler profiles.

    Args:
        y: Audio time series as numpy array.
        sr: Sampling rate of the audio.

    Returns:
        Dictionary with keys:
            - "key": Key name as string (e.g., "C major", "A minor", "unknown")
            - "confidence": Float between 0.0 and 1.0 indicating confidence in the detection
    """
    try:
        # Handle edge cases
        if len(y) == 0:
            return {"name": "unknown", "confidence": float(0.0)}

        # Compute chromagram using CQT-based chroma features
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)

        # Aggregate chromagram over time (mean across frames)
        chroma_mean = np.mean(chroma, axis=1)

        # Normalize chroma vector
        if np.sum(chroma_mean) > 0:
            chroma_mean = chroma_mean / np.sum(chroma_mean)
        else:
            return {"name": "unknown", "confidence": float(0.0)}

        # Compare against all 24 profiles
        best_key = "unknown"
        best_mode = "major"
        best_correlation = -1.0

        # Try major keys
        for pitch in PITCH_NAMES:
            profile = np.array(MAJOR_PROFILES[pitch])
            # Normalize profile
            profile = profile / np.sum(profile)
            # Compute Pearson correlation
            try:
                correlation, _ = pearsonr(chroma_mean, profile)
                if correlation > best_correlation:
                    best_correlation = correlation
                    best_key = pitch
                    best_mode = "major"
            except Exception:
                # Skip comparison if correlation fails
                pass

        # Try minor keys
        for pitch in PITCH_NAMES:
            profile = np.array(MINOR_PROFILES[pitch])
            # Normalize profile
            profile = profile / np.sum(profile)
            try:
                correlation, _ = pearsonr(chroma_mean, profile)
                if correlation > best_correlation:
                    best_correlation = correlation
                    best_key = pitch
                    best_mode = "minor"
            except Exception:
                pass

        # Normalize correlation to confidence (correlation ranges from -1 to 1)
        # Map to 0.0-1.0 range
        confidence = float(max(0.0, (best_correlation + 1.0) / 2.0))

        if best_key != "unknown":
            return {"name": f"{best_key} {best_mode}", "confidence": confidence}
        else:
            return {"name": "unknown", "confidence": float(0.0)}

    except Exception:
        # Fallback for any unexpected errors
        return {"name": "unknown", "confidence": float(0.0)}


def analyze_midi(mid):
    """Placeholder for MIDI key detection (not implemented in audio module)."""
    return {"name": "unknown", "confidence": float(0.0)}
