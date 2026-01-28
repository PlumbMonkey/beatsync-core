import bpy
from beatsync_blender_visual_core.drivers import marker_to_driver_expr

class BEATSYNC_OT_add_marker_driver(bpy.types.Operator):
	bl_idname = "beatsync.add_marker_driver"
	bl_label = "Add Driver to Selected Object"
	bl_description = "Add a driver to the selected object based on BeatSync marker."

	marker_frame: bpy.props.IntProperty(name="Marker Frame", default=1)
	prop_name: bpy.props.StringProperty(name="Property Name", default="location.x")

	def execute(self, context):
		obj = context.active_object
		if obj is None:
			self.report({'ERROR'}, "No active object selected.")
			return {'CANCELLED'}
		try:
			fcurve = obj.driver_add(self.prop_name)
			driver = fcurve.driver
			driver.type = 'SCRIPTED'
			expr = marker_to_driver_expr({"frame": self.marker_frame, "name": "marker"}, self.prop_name)
			driver.expression = expr
			self.report({'INFO'}, f"Driver added: {expr}")
			return {'FINISHED'}
		except Exception as e:
			self.report({'ERROR'}, str(e))
			return {'CANCELLED'}
