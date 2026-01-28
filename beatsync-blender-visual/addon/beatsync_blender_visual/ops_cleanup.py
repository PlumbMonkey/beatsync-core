import bpy

class BEATSYNC_OT_cleanup_beatsync(bpy.types.Operator):
	bl_idname = "beatsync.cleanup_beatsync"
	bl_label = "Cleanup BeatSync Markers and Drivers"
	bl_description = "Remove all BeatSync markers and drivers from the scene."

	def execute(self, context):
		# Remove all timeline markers with names starting with 'Beat'
		scene = context.scene
		to_remove = [m for m in scene.timeline_markers if m.name.startswith("Beat")]
		for m in to_remove:
			scene.timeline_markers.remove(m)
		# Remove drivers from all objects that match BeatSync pattern
		for obj in scene.objects:
			if obj.animation_data and obj.animation_data.drivers:
				for fcurve in list(obj.animation_data.drivers):
					if "BeatSync" in fcurve.data_path or "location" in fcurve.data_path:
						obj.animation_data.drivers.remove(fcurve)
		self.report({'INFO'}, f"Removed {len(to_remove)} markers and drivers.")
		return {'FINISHED'}
