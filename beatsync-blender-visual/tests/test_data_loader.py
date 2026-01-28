

import pytest
from beatsync_blender_visual_core.data_loader import BeatSyncData, validate_beatsync_json

def test_valid_json_loads():
    data = {
        "tempo": 120,
        "markers": [{"name": "A", "frame": 1}],
        "energy": [0.1, 0.2],
        "key": "C"
    }
    assert validate_beatsync_json(data)
    model = BeatSyncData.from_json(data)
    assert model.tempo == 120
    assert model.markers[0]["name"] == "A"
    assert model.energy == [0.1, 0.2]
    assert model.key == "C"

def test_invalid_schema_fails():
    with pytest.raises(ValueError):
        validate_beatsync_json({"foo": 1})
