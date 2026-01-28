from beatsync_blender_visual_core import driver_expr

def test_driver_expr_for_marker():
    expr = driver_expr.driver_expr_for_marker(42)
    assert "frame == 42" in expr
    assert expr.startswith("clamp(")
    assert expr.endswith(", 0.0, 1.0)")
    expr2 = driver_expr.driver_expr_for_marker(10, clamp_min=-1, clamp_max=2)
    assert ", -1, 2)" in expr2
