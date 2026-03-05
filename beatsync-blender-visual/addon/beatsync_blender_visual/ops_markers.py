"""Marker-related Blender operators."""
import bpy


class BEATSYNC_OT_place_markers(bpy.types.Operator):
    """Place timeline markers at BeatSync beat positions."""

    bl_idname = "beatsync.place_markers"
    bl_label = "Place Beat Markers"
    bl_description = "Place timeline markers at each beat position from loaded BeatSync JSON"

    def execute(self, context):
        """Place markers at beat timestamps converted to frame numbers."""
        scene = context.scene

        # Retrieve loaded BeatSync JSON data as string from scene
        beatsync_json_str = getattr(scene, 'beatsync_json_data', None)
        if not beatsync_json_str:
            self.report({'ERROR'}, "No BeatSync JSON data loaded. Import JSON first.")
            return {'CANCELLED'}

        # Parse JSON (already validated during import)
        import json
        try:
            beatsync_data = json.loads(beatsync_json_str)
        except Exception as e:
            self.report({'ERROR'}, f"Failed to parse BeatSync JSON: {str(e)}")
            return {'CANCELLED'}

        # Extract beats and FPS
        beats = beatsync_data.get('beats', [])
        if not beats:
            self.report({'ERROR'}, "No beats found in BeatSync JSON.")
            return {'CANCELLED'}

        fps = scene.render.fps
        marker_count = 0

        # Place a marker at each beat timestamp
        for i, beat in enumerate(beats):
            # Each beat is a timestamp in seconds
            beat_time = beat if isinstance(beat, (int, float)) else beat.get('time', 0.0)
            frame = round(beat_time * fps)

            # Create marker with descriptive name
            marker_name = f"Beat_{i}"
            scene.timeline_markers.new(name=marker_name, frame=frame)
            marker_count += 1

        self.report({'INFO'}, f"Placed {marker_count} beat markers.")
        return {'FINISHED'}
