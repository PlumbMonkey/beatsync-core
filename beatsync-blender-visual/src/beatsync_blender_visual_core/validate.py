def validate_beatsync_json(data):
    if not isinstance(data, dict):
        raise ValueError("Input must be a dict")
    if "markers" not in data:
        raise ValueError("Missing 'markers' key")
    if not isinstance(data["markers"], list):
        raise ValueError("'markers' must be a list")
    for marker in data["markers"]:
        if not isinstance(marker, dict):
            raise ValueError("Each marker must be a dict")
        if "name" not in marker or "frame" not in marker:
            raise ValueError("Each marker must have 'name' and 'frame'")
    return True
