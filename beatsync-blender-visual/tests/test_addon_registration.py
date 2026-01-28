import importlib.util
import pytest

if importlib.util.find_spec("bpy") is None:
    pytest.skip("Add-on registration requires Blender (bpy). Run Blender smoke tests.", allow_module_level=True)

def test_addon_registration_imports():
    # This test ensures the Blender add-on can be imported for registration (no bpy test)
    spec = importlib.util.spec_from_file_location(
        "beatsync_blender_visual",
        "./beatsync-blender-visual/addon/beatsync_blender_visual/__init__.py"
    )
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert hasattr(module, "register")
    assert hasattr(module, "unregister")
