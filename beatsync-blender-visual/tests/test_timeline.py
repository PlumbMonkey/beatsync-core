from beatsync_blender_visual_core import timeline
import pytest

def test_bpm_to_frame():
    assert timeline.bpm_to_frame(120, 1.0, 24) == 24
    assert timeline.bpm_to_frame(60, 2.0, 30) == 60
    with pytest.raises(ValueError):
        timeline.bpm_to_frame(0, 1.0, 24)
    with pytest.raises(ValueError):
        timeline.bpm_to_frame(120, 1.0, 0)

def test_marker_timestamp_to_frame():
    assert timeline.marker_timestamp_to_frame({"frame": 42}, 24) == 42
    assert timeline.marker_timestamp_to_frame({"time": 2.5}, 24) == 60
    with pytest.raises(ValueError):
        timeline.marker_timestamp_to_frame({}, 24)
