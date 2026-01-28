import bpy
import json
from beatsync_blender_visual_core.validate import validate_beatsync_json

class BEATSYNC_OT_import_json(bpy.types.Operator):
    bl_idname = "beatsync.import_json"
    bl_label = "Import BeatSync JSON"
    bl_description = "Import a BeatSync JSON file and add timeline markers."

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    name_filter: bpy.props.StringProperty(
        name="Name Filter",
        description="Only import markers whose name contains this substring (leave blank for all)",
        default=""
    )

    def execute(self, context):
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            validate_beatsync_json(data)
            markers = data.get('markers', [])
            scene = context.scene
            count = 0
            for marker in markers:
                name = marker.get('name', 'BS')
                frame = marker.get('frame', 0)
                if self.name_filter and self.name_filter not in name:
                    continue
                scene.timeline_markers.new(name=name, frame=frame)
                count += 1
            self.report({'INFO'}, f"Imported {count} markers.")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
