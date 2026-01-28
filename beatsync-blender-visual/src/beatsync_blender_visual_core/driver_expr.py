def driver_expr_for_marker(marker_frame, prop_name="location.x", clamp_min=0.0, clamp_max=1.0):
    """
    Generate a Blender driver expression string for a property, clamped to bounds.
    Example: 'clamp(1.0 if frame == 42 else 0.0, 0.0, 1.0)'
    """
    expr = f"1.0 if frame == {marker_frame} else 0.0"
    return f"clamp({expr}, {clamp_min}, {clamp_max})"
