import json
import bpy

def import_beatsync_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    markers = data.get('markers', [])
    scene = bpy.context.scene
    for marker in markers:
        name = marker.get('name', 'BS')
        frame = marker.get('frame', 0)
        m = scene.timeline_markers.new(name=name, frame=frame)
    return len(markers)
