import json

def validate_beatsync_json(data):
    if not isinstance(data, dict):
        raise ValueError("Input must be a dict")
    if "markers" not in data:
        raise ValueError("Missing 'markers' key")
    if not isinstance(data["markers"], list):
        raise ValueError("'markers' must be a list")
    # Optional: check for tempo, energy, key
    return True

class BeatSyncData:
    def __init__(self, tempo=None, markers=None, energy=None, key=None):
        self.tempo = tempo
        self.markers = markers or []
        self.energy = energy
        self.key = key

    @classmethod
    def from_json(cls, json_data):
        validate_beatsync_json(json_data)
        return cls(
            tempo=json_data.get("tempo"),
            markers=json_data.get("markers", []),
            energy=json_data.get("energy"),
            key=json_data.get("key"),
        )
