# Minimal UI panel for BeatSync Blender Visual (Phase 3.5)
import bpy


class BEATSYNC_PT_main(bpy.types.Panel):
    """Main BeatSync panel in VIEW_3D."""

    bl_label = "BeatSync"
    bl_idname = "BEATSYNC_PT_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BeatSync'

    def draw(self, context):
        layout = self.layout
        layout.label(text="BeatSync Add-on Loaded!")

        # Import and data management
        layout.operator("beatsync.import_json", text="Import BeatSync JSON")

        # Marker and driver operations
        layout.operator("beatsync.place_markers", text="Place Beat Markers")
        layout.operator("beatsync.add_marker_driver", text="Add Driver to Selected Object")

        # Cleanup
        layout.operator("beatsync.cleanup_beatsync", text="Cleanup BeatSync Markers/Drivers")

        # Status readout
        scene = context.scene
        status = getattr(scene, 'beatsync_status', 'No data loaded')
        layout.label(text=f"Status: {status}")
