from beatsync_blender_visual_core import naming

def test_normalize_marker_name():
    assert naming.normalize_marker_name("  Beat 1  ") == "Beat 1"
    assert naming.normalize_marker_name("A" * 100) == "A" * 64
