"""MIDI key detection using pitch class histogram and Krumhansl-Schmuckler profiles."""
import numpy as np
from scipy.stats import pearsonr


# Krumhansl-Schmuckler profiles for major and minor keys
# Profiles for all 12 pitch classes: C, C#, D, D#, E, F, F#, G, G#, A, A#, B
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


def detect_key(midi) -> dict:
    """
    Detect the key of a MIDI file using pitch class histogram.

    Args:
        midi: A mido.MidiFile object.

    Returns:
        Dictionary with keys:
            - "key": Key name as string (e.g., "C major", "A minor", "unknown")
            - "confidence": Float between 0.0 and 0.85 indicating confidence
                           in the detection (capped at 0.85 for MIDI)
    """
    try:
        # Handle None/empty MIDI
        if midi is None or not hasattr(midi, 'tracks'):
            return {"key": "unknown", "confidence": 0.0}

        # Extract pitch class histogram from all notes
        pitch_counts = np.zeros(12)
        note_count = 0

        for track in midi.tracks:
            for msg in track:
                # Count note_on events
                if msg.type == 'note_on' and msg.velocity > 0:
                    pitch_class = msg.note % 12
                    pitch_counts[pitch_class] += msg.velocity  # Weight by velocity
                    note_count += 1

        # Handle empty MIDI
        if note_count == 0:
            return {"key": "unknown", "confidence": 0.0}

        # Normalize pitch class distribution
        pitch_histogram = pitch_counts / np.sum(pitch_counts)

        # Compare against all 24 profiles
        best_key = "unknown"
        best_mode = "major"
        best_correlation = -1.0

        # Try major keys
        for pitch in PITCH_NAMES:
            profile = np.array(MAJOR_PROFILES[pitch])
            # Normalize profile
            profile = profile / np.sum(profile)
            try:
                correlation, _ = pearsonr(pitch_histogram, profile)
                if correlation > best_correlation:
                    best_correlation = correlation
                    best_key = pitch
                    best_mode = "major"
            except Exception:
                pass

        # Try minor keys
        for pitch in PITCH_NAMES:
            profile = np.array(MINOR_PROFILES[pitch])
            profile = profile / np.sum(profile)
            try:
                correlation, _ = pearsonr(pitch_histogram, profile)
                if correlation > best_correlation:
                    best_correlation = correlation
                    best_key = pitch
                    best_mode = "minor"
            except Exception:
                pass

        # Normalize correlation to confidence (correlation ranges from -1 to 1)
        # Map to 0.0-0.85 range (MIDI detection is less reliable than audio)
        confidence = max(0.0, (best_correlation + 1.0) / 2.0)
        # Cap MIDI confidence at 0.85 since it's less reliable than audio
        confidence = min(0.85, confidence)

        if best_key != "unknown":
            return {"key": f"{best_key} {best_mode}", "confidence": confidence}
        else:
            return {"key": "unknown", "confidence": 0.0}

    except Exception:
        # Fallback for any unexpected errors
        return {"key": "unknown", "confidence": 0.0}
