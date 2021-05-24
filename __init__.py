bl_info = {"name": "Panda3DTools", 
           "description": "A set of utilities for exporting from blender to the panda environment.",
           "author": "Sergei Korotkov",
           "version": (0, 1),
           "blender": (2, 80, 0),
           "location": "UI", 
           "warning": "Alpha testing",
           "support": "COMMUNITY",
           "wiki_url": "https://github.com/serkkz/PandaTools/wiki", 
           "tracker_url": "https://github.com/serkkz/PandaTools/issues",
           "category": "Panda3D"}

import bpy

try:
    import panda3d
    status = True
except ImportError: 
    status = False

if status:

    from .interface import Setting, Mesh, Scene, Camera, Light, Selected
    from .logic import ExportObject, ExportScene, ExportSelected, CheckingCoplanarity, CheckingQuad

    from bpy.props import StringProperty, BoolProperty, EnumProperty, IntProperty
    from bpy.types import PropertyGroup


    class ObjectExtended(PropertyGroup):

        rel_path_object : StringProperty(subtype = 'NONE', default = 'Object')

        type_mesh : EnumProperty(items=(('Render', "Render", "Geometry that is being rendered"),
                                        ('Collision', "Collision", "Panda3D collision system")),
                                        default='Render')

        coordinate_system : EnumProperty(items=(('CS_default', "CS_default", "The value from the configuration file will be used"),
                                                ('CS_zup_right', "CS_zup_right", "Z-Up, Right-handed"), ('CS_yup_right', "CS_yup_right", "Y-Up, Right-handed"),
                                                ('CS_zup_left', "CS_zup_left", "Z-Up, Left-handed"), ('CS_yup_left', "CS_yup_leftp", "Y-Up, Left-handed"),
                                                ('CS_invalid', "CS_invalid", "Custom processing code to indicate a contradictory coordinate system")), default='CS_yup_right')

        camera_active : BoolProperty(name="Сamera active", description = "When the camera is not active, nothing will be rendered", default = True)
        visibility_collision_polygons : BoolProperty(name="Visibility", description = "This flag shows collision polygons", default = False)

        draw_mask_1 : StringProperty(subtype = 'BYTE_STRING', maxlen = 4, name = "Draw mask", default = '0111')
        draw_mask_2 : StringProperty(subtype = 'BYTE_STRING', maxlen = 4, name = "Draw mask", default = '1111')
        draw_mask_3 : StringProperty(subtype = 'BYTE_STRING', maxlen = 4, name = "Draw mask", default = '1111')
        draw_mask_4 : StringProperty(subtype = 'BYTE_STRING', maxlen = 4, name = "Draw mask", default = '1111')
        draw_mask_5 : StringProperty(subtype = 'BYTE_STRING', maxlen = 4, name = "Draw mask", default = '1111')
        draw_mask_6 : StringProperty(subtype = 'BYTE_STRING', maxlen = 4, name = "Draw mask", default = '1111')
        draw_mask_7 : StringProperty(subtype = 'BYTE_STRING', maxlen = 4, name = "Draw mask", default = '1111')
        draw_mask_8 : StringProperty(subtype = 'BYTE_STRING', maxlen = 4, name = "Draw mask", default = '1111')

        from_mask_1 : StringProperty(subtype = 'BYTE_STRING', maxlen = 4, name = "Collision mask", default = '0000')
        from_mask_2 : StringProperty(subtype = 'BYTE_STRING', maxlen = 4, name = "Collision mask", default = '0000')
        from_mask_3 : StringProperty(subtype = 'BYTE_STRING', maxlen = 4, name = "Collision mask", default = '0000')
        from_mask_4 : StringProperty(subtype = 'BYTE_STRING', maxlen = 4, name = "Collision mask", default = '1111')
        from_mask_5 : StringProperty(subtype = 'BYTE_STRING', maxlen = 4, name = "Collision mask", default = '1111')
        from_mask_6 : StringProperty(subtype = 'BYTE_STRING', maxlen = 4, name = "Collision mask", default = '1111')
        from_mask_7 : StringProperty(subtype = 'BYTE_STRING', maxlen = 4, name = "Collision mask", default = '1111')
        from_mask_8 : StringProperty(subtype = 'BYTE_STRING', maxlen = 4, name = "Collision mask", default = '1111')
        
        into_mask_1 : StringProperty(subtype = 'BYTE_STRING', maxlen = 4, name = "Collision mask", default = '0000')
        into_mask_2 : StringProperty(subtype = 'BYTE_STRING', maxlen = 4, name = "Collision mask", default = '0000')
        into_mask_3 : StringProperty(subtype = 'BYTE_STRING', maxlen = 4, name = "Collision mask", default = '0000')
        into_mask_4 : StringProperty(subtype = 'BYTE_STRING', maxlen = 4, name = "Collision mask", default = '1111')
        into_mask_5 : StringProperty(subtype = 'BYTE_STRING', maxlen = 4, name = "Collision mask", default = '1111')
        into_mask_6 : StringProperty(subtype = 'BYTE_STRING', maxlen = 4, name = "Collision mask", default = '1111')
        into_mask_7 : StringProperty(subtype = 'BYTE_STRING', maxlen = 4, name = "Collision mask", default = '1111')
        into_mask_8 : StringProperty(subtype = 'BYTE_STRING', maxlen = 4, name = "Collision mask", default = '1111')

    class SceneExtended(PropertyGroup):

        ful_path_project : StringProperty(subtype = 'DIR_PATH', default = 'D:/mygame/')
        rel_path_scene : StringProperty(subtype = 'NONE', default = 'Scene')
        rel_path_other : StringProperty(subtype = 'NONE', default = 'Other')

        file_name_selected : StringProperty(subtype = 'NONE', default = '')

    classes = (
        Setting,
        Mesh,
        Scene,
        Camera,
        Light,
        Selected,

        ObjectExtended,
        SceneExtended,

        ExportObject,
        ExportScene,
        ExportSelected,
        CheckingCoplanarity,
        CheckingQuad,
    )

    def register():

        from bpy.utils import register_class

        for cls in classes:
            register_class(cls)

        bpy.types.Scene.hatcher = bpy.props.PointerProperty(type = SceneExtended)
        bpy.types.Object.hatcher = bpy.props.PointerProperty(type = ObjectExtended)

    def unregister():

        from bpy.utils import unregister_class

        for cls in reversed(classes):
            unregister_class(cls)

        del bpy.types.Scene.hatcher
        del bpy.types.Object.hatcher
        
else:

    class Message(bpy.types.Panel):
        bl_idname = "MESSAGE_PT_Panel"
        bl_label = "Message"
        bl_category = "Panda3DTools"
        bl_space_type = 'VIEW_3D'
        bl_region_type = 'UI'

        def draw(self, context):
            layout = self.layout
            layout.label(text='The Panda3D package is not installed in the blender')
            layout.label(text='Refer to the plugin documentation.')
            op = layout.operator('wm.url_open', text='Open Wiki', icon='URL')
            op.url = 'https://github.com/serkkz/Panda3DTools/wiki/Installation'

    classes = (
        Message,
    )

    def register():

        from bpy.utils import register_class

        for cls in classes:
            register_class(cls)

    def unregister():

        from bpy.utils import unregister_class

        for cls in reversed(classes):
            unregister_class(cls)