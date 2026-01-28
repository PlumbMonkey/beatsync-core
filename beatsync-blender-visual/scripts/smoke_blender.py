import sys
import os

# Add the add-on directory to sys.path
addon_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../addon'))
if addon_dir not in sys.path:
    sys.path.insert(0, addon_dir)

import bpy

# Enable the BeatSync add-on
try:
    bpy.ops.preferences.addon_enable(module="beatsync_blender_visual")
    print("[BEATSYNC] Add-on enabled successfully.")
except Exception as e:
    print(f"[BEATSYNC] Failed to enable add-on: {e}")
    sys.exit(1)

# Run the import operator with a test fixture
fixture = os.path.abspath(os.path.join(os.path.dirname(__file__), '../fixtures/beatsync_test_markers.json'))
try:
    result = bpy.ops.beatsync.import_json('INVOKE_DEFAULT', filepath=fixture)
    print(f"[BEATSYNC] Import operator result: {result}")
except Exception as e:
    print(f"[BEATSYNC] Import operator failed: {e}")
    sys.exit(1)

print("[BEATSYNC] Smoke test completed.")
sys.exit(0)
