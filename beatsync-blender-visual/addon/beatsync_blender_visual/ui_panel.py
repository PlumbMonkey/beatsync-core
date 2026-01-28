import bpy

from .ops_import import BEATSYNC_OT_import_json
import bpy

class BeatSyncPanel(bpy.types.Panel):
    bl_label = "BeatSync"
    bl_idname = "BEATSYNC_PT_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BeatSync'

    def draw(self, context):
        layout = self.layout
        layout.label(text="BeatSync Add-on Loaded!")
        layout.operator("beatsync.import_json", text="Import BeatSync JSON")
        layout.operator("beatsync.add_marker_driver", text="Add Driver to Selected Object")
        layout.operator("beatsync.cleanup_beatsync", text="Cleanup BeatSync Markers/Drivers")
