import bpy
import sys
import os

# Add the add-on directory to sys.path
addon_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../addon'))
if addon_dir not in sys.path:
    sys.path.insert(0, addon_dir)

# Enable the BeatSync add-on
try:
    bpy.ops.preferences.addon_enable(module="beatsync_blender_visual")
    print("[BEATSYNC] Add-on enabled successfully.")
except Exception as e:
    print(f"[BEATSYNC] Failed to enable add-on: {e}")
    sys.exit(1)

# Optionally: import a test JSON and run marker/driver ops here
# ...

# Save the .blend file for regression comparison
output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../fixtures/regression_output.blend'))
bpy.ops.wm.save_as_mainfile(filepath=output_path)
print(f"[BEATSYNC] Saved regression .blend to {output_path}")
sys.exit(0)
