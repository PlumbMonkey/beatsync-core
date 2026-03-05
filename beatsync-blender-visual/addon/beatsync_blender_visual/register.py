"""Registration and unregistration of BeatSync Blender add-on classes."""


def register():
    """Register all BeatSync classes with Blender."""
    import bpy
    from .ui_panel import BEATSYNC_PT_main
    from .ops_import import BEATSYNC_OT_import_json
    from .ops_markers import BEATSYNC_OT_place_markers
    from .ops_drivers import BEATSYNC_OT_add_marker_driver
    from .ops_cleanup import BEATSYNC_OT_cleanup_beatsync

    # Register panel
    bpy.utils.register_class(BEATSYNC_PT_main)

    # Register operators
    bpy.utils.register_class(BEATSYNC_OT_import_json)
    bpy.utils.register_class(BEATSYNC_OT_place_markers)
    bpy.utils.register_class(BEATSYNC_OT_add_marker_driver)
    bpy.utils.register_class(BEATSYNC_OT_cleanup_beatsync)


def unregister():
    """Unregister all BeatSync classes from Blender."""
    import bpy
    from .ui_panel import BEATSYNC_PT_main
    from .ops_import import BEATSYNC_OT_import_json
    from .ops_markers import BEATSYNC_OT_place_markers
    from .ops_drivers import BEATSYNC_OT_add_marker_driver
    from .ops_cleanup import BEATSYNC_OT_cleanup_beatsync

    # Unregister operators (in reverse order of registration)
    bpy.utils.unregister_class(BEATSYNC_OT_cleanup_beatsync)
    bpy.utils.unregister_class(BEATSYNC_OT_add_marker_driver)
    bpy.utils.unregister_class(BEATSYNC_OT_place_markers)
    bpy.utils.unregister_class(BEATSYNC_OT_import_json)

    # Unregister panel
    bpy.utils.unregister_class(BEATSYNC_PT_main)
