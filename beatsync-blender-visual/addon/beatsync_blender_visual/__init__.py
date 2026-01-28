
from .bl_info import bl_info
from .ui_panel import BeatSyncPanel
from .ops_import import BEATSYNC_OT_import_json
from .ops_drivers import BEATSYNC_OT_add_marker_driver
from .ops_cleanup import BEATSYNC_OT_cleanup_beatsync

import bpy


def register():
    bpy.utils.register_class(BEATSYNC_OT_import_json)
    bpy.utils.register_class(BEATSYNC_OT_add_marker_driver)
    bpy.utils.register_class(BEATSYNC_OT_cleanup_beatsync)
    bpy.utils.register_class(BeatSyncPanel)


def unregister():
    bpy.utils.unregister_class(BeatSyncPanel)
    bpy.utils.unregister_class(BEATSYNC_OT_cleanup_beatsync)
    bpy.utils.unregister_class(BEATSYNC_OT_add_marker_driver)
    bpy.utils.unregister_class(BEATSYNC_OT_import_json)
