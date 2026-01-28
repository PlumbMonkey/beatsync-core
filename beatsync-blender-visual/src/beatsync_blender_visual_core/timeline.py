def bpm_to_frame(bpm, time_seconds, fps):
    """Convert a time in seconds to a frame number, given BPM and FPS."""
    if bpm <= 0 or fps <= 0:
        raise ValueError("BPM and FPS must be positive")
    beats_per_second = bpm / 60.0
    return round(time_seconds * fps)

def marker_timestamp_to_frame(marker, fps):
    """Convert a marker's timestamp (in seconds or frame) to a frame number."""
    # If marker has 'frame', use it directly; else, convert 'time' to frame
    if "frame" in marker:
        return int(marker["frame"])
    elif "time" in marker:
        return round(marker["time"] * fps)
    else:
        raise ValueError("Marker must have 'frame' or 'time'")
