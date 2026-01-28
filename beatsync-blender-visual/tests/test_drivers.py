from beatsync_blender_visual_core import drivers

def test_marker_to_driver_expr():
    marker = {"name": "Beat 1", "frame": 42}
    expr = drivers.marker_to_driver_expr(marker)
    assert "42" in expr
    assert "1.0 if frame == 42 else 0.0" == expr
