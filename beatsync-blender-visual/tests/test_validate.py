from beatsync_blender_visual_core import validate
import pytest

def test_validate_good():
    data = {"markers": [
        {"name": "A", "frame": 1},
        {"name": "B", "frame": 2}
    ]}
    assert validate.validate_beatsync_json(data) is True

def test_validate_missing_markers():
    with pytest.raises(ValueError):
        validate.validate_beatsync_json({})

def test_validate_bad_marker():
    data = {"markers": [
        {"name": "A"}  # missing frame
    ]}
    with pytest.raises(ValueError):
        validate.validate_beatsync_json(data)
