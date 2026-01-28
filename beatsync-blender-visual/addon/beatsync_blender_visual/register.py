def register():
    import bpy
    from .ui_panel import BEATSYNC_PT_main
    bpy.utils.register_class(BEATSYNC_PT_main)

def unregister():
    import bpy
    from .ui_panel import BEATSYNC_PT_main
    bpy.utils.unregister_class(BEATSYNC_PT_main)
