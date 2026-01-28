from beatsync_blender_visual_core import mapping

def test_marker_json_to_blender():
    marker = {"name": "Beat 1", "frame": 42}
    result = mapping.marker_json_to_blender(marker)
    assert result == {"name": "Beat 1", "frame": 42}
