import bpy

class Setting(bpy.types.Panel):
    bl_idname = "SETTING_PT_Panel"
    bl_label = "Settings"
    bl_category = "Panda3DTools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout

        layout.prop(context.scene.hatcher, 'ful_path_project', text='Directory project')

        # Если список выбранных объектов пуст.
        if context.selected_objects == []:
            layout.prop(context.scene.hatcher, 'rel_path_scene', text='Relative catalog')
        # Если нет.
        else:
            # Проверяем количество объектов.
            if len(context.selected_objects) >=2:
                layout.prop(context.scene.hatcher, 'rel_path_other', text='Relative catalog')
            else:
                layout.prop(context.object.hatcher, 'rel_path_object', text='Relative catalog')


class Selected(bpy.types.Panel):
    bl_idname = "SELECTED_PT_Panel"
    bl_label = "Selected"
    bl_category = "Panda3DTools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    @classmethod
    def poll(cls, context):
        return (len(context.selected_objects) >=2)

    def draw(self, context):
        layout = self.layout

        layout.prop(context.scene.hatcher, "file_name_selected", text='File name')

        main = layout.row()

        export_selected = main.row(align = True)

        if not context.scene.hatcher.file_name_selected == '':
            export_selected.operator("ui.export_selected", text="Export selected with merge.")
        else:
            export_selected.operator("ui.export_selected", text="Export selected separately.")

class Scene(bpy.types.Panel):
    bl_idname = "SCENE_PT_Panel"
    bl_label = "Scene"
    bl_category = "Panda3DTools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    @classmethod
    def poll(cls, context):
        return (context.selected_objects == [])

    def draw(self, context):
        layout = self.layout

        layout.prop(context.scene, "name", text='File name')

        main = layout.row()

        export_scene = main.row(align = True)
        export_scene.operator("ui.export_scene", text="Export scene")


class Mesh(bpy.types.Panel):
    bl_idname = "MESH_PT_Panel"
    bl_label = "Mesh"
    bl_category = "Panda3DTools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    @classmethod
    def poll(cls, context):
        return (context.active_object is not None and
                context.active_object.type == 'MESH' and
                context.selected_objects != [] and
                len(context.selected_objects) <=1)

    def draw(self, context):
        layout = self.layout
        
        layout.prop(context.object.hatcher, "type_mesh", text="Mesh type")

        layout.prop(context.object, "name", text='File name')
        
        main = layout.row()

        options = layout.box()

        if context.object.hatcher.type_mesh == "Render":
        
            export_objects = main.row(align = True)
            
            export_objects.operator("ui.export_object", text="Export Mesh")
            
            mask = options.split()
            
            mask.label(text='Mask draw:')

            mask.prop(context.object.hatcher, "draw_mask_1", text = "")
            mask.prop(context.object.hatcher, "draw_mask_2", text = "")
            mask.prop(context.object.hatcher, "draw_mask_3", text = "")
            mask.prop(context.object.hatcher, "draw_mask_4", text = "")
            mask.prop(context.object.hatcher, "draw_mask_5", text = "")
            mask.prop(context.object.hatcher, "draw_mask_6", text = "")
            mask.prop(context.object.hatcher, "draw_mask_7", text = "")
            mask.prop(context.object.hatcher, "draw_mask_8", text = "")

        if context.object.hatcher.type_mesh == "Collision":

            export_objects = main.row(align = True)

            functions = export_objects.split()
            functions.operator("ui.check_quad", text="Checking not Quad")
            functions.operator("ui.check_coplanarity", text="Checking not Coplanarity")
            functions.operator("ui.export_object", text="Export Collision")

            # Если есть слоты материала.
            if len(context.object.data.materials) >> 0:
                if hasattr(context.object.active_material, 'name'):
                    options.prop(context.object.active_material.hatcher, "visibility_collision_polygons", text = "Show collision polygons")

                    mask = options.split()

                    mask.label(text='Mask from:')

                    mask.prop(context.object.active_material.hatcher, "from_mask_1", text = "")
                    mask.prop(context.object.active_material.hatcher, "from_mask_2", text = "")
                    mask.prop(context.object.active_material.hatcher, "from_mask_3", text = "")
                    mask.prop(context.object.active_material.hatcher, "from_mask_4", text = "")
                    mask.prop(context.object.active_material.hatcher, "from_mask_5", text = "")
                    mask.prop(context.object.active_material.hatcher, "from_mask_6", text = "")
                    mask.prop(context.object.active_material.hatcher, "from_mask_7", text = "")
                    mask.prop(context.object.active_material.hatcher, "from_mask_8", text = "")
                    
                    mask = options.split()

                    mask.label(text='Mask into:')

                    mask.prop(context.object.active_material.hatcher, "into_mask_1", text = "")
                    mask.prop(context.object.active_material.hatcher, "into_mask_2", text = "")
                    mask.prop(context.object.active_material.hatcher, "into_mask_3", text = "")
                    mask.prop(context.object.active_material.hatcher, "into_mask_4", text = "")
                    mask.prop(context.object.active_material.hatcher, "into_mask_5", text = "")
                    mask.prop(context.object.active_material.hatcher, "into_mask_6", text = "")
                    mask.prop(context.object.active_material.hatcher, "into_mask_7", text = "")
                    mask.prop(context.object.active_material.hatcher, "into_mask_8", text = "")
                
                else:

                    options.prop(context.object.hatcher, "visibility_collision_polygons", text = "Show collision polygons")

                    mask = options.split()

                    mask.label(text='Mask from:')

                    mask.prop(context.object.hatcher, "from_mask_1", text = "")
                    mask.prop(context.object.hatcher, "from_mask_2", text = "")
                    mask.prop(context.object.hatcher, "from_mask_3", text = "")
                    mask.prop(context.object.hatcher, "from_mask_4", text = "")
                    mask.prop(context.object.hatcher, "from_mask_5", text = "")
                    mask.prop(context.object.hatcher, "from_mask_6", text = "")
                    mask.prop(context.object.hatcher, "from_mask_7", text = "")
                    mask.prop(context.object.hatcher, "from_mask_8", text = "")
                    
                    mask = options.split()

                    mask.label(text='Mask into:')

                    mask.prop(context.object.hatcher, "into_mask_1", text = "")
                    mask.prop(context.object.hatcher, "into_mask_2", text = "")
                    mask.prop(context.object.hatcher, "into_mask_3", text = "")
                    mask.prop(context.object.hatcher, "into_mask_4", text = "")
                    mask.prop(context.object.hatcher, "into_mask_5", text = "")
                    mask.prop(context.object.hatcher, "into_mask_6", text = "")
                    mask.prop(context.object.hatcher, "into_mask_7", text = "")
                    mask.prop(context.object.hatcher, "into_mask_8", text = "")
                
            else:
                options.prop(context.object.hatcher, "visibility_collision_polygons", text = "Show collision polygons")

                mask = options.split()

                mask.label(text='Mask from:')

                mask.prop(context.object.hatcher, "from_mask_1", text = "")
                mask.prop(context.object.hatcher, "from_mask_2", text = "")
                mask.prop(context.object.hatcher, "from_mask_3", text = "")
                mask.prop(context.object.hatcher, "from_mask_4", text = "")
                mask.prop(context.object.hatcher, "from_mask_5", text = "")
                mask.prop(context.object.hatcher, "from_mask_6", text = "")
                mask.prop(context.object.hatcher, "from_mask_7", text = "")
                mask.prop(context.object.hatcher, "from_mask_8", text = "")
                
                mask = options.split()

                mask.label(text='Mask into:')

                mask.prop(context.object.hatcher, "into_mask_1", text = "")
                mask.prop(context.object.hatcher, "into_mask_2", text = "")
                mask.prop(context.object.hatcher, "into_mask_3", text = "")
                mask.prop(context.object.hatcher, "into_mask_4", text = "")
                mask.prop(context.object.hatcher, "into_mask_5", text = "")
                mask.prop(context.object.hatcher, "into_mask_6", text = "")
                mask.prop(context.object.hatcher, "into_mask_7", text = "")
                mask.prop(context.object.hatcher, "into_mask_8", text = "")

        if context.mode == 'EDIT_MESH':
            export_objects.enabled = False


class Camera(bpy.types.Panel):
    bl_idname = "CAMERA_PT_Panel"
    bl_label = "Camera"
    bl_category = "Panda3DTools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    @classmethod
    def poll(cls, context):
        return (context.active_object is not None and
                context.active_object.type == 'CAMERA' and
                context.selected_objects != [] and
                len(context.selected_objects) <=1)

    def draw(self, context):

        layout = self.layout

        layout.prop(context.object, "name", text='File name')

        main = layout.row()

        export_objects = main.row(align = True)
        export_objects.operator("ui.export_object", text="Export camera")

        if context.active_object.data.type == 'PANO':
            layout.label(text='This type of lens is not supported!')
            export_objects.enabled = False

        options = layout.box()

        options.prop(context.object.hatcher, "camera_active", text = "Сamera active")

        options.prop(context.object.hatcher, "coordinate_system", text = "Сoordinate system")

        mask = options.split()

        mask.label(text='Mask draw:')

        mask.prop(context.object.hatcher, "draw_mask_1", text = "")
        mask.prop(context.object.hatcher, "draw_mask_2", text = "")
        mask.prop(context.object.hatcher, "draw_mask_3", text = "")
        mask.prop(context.object.hatcher, "draw_mask_4", text = "")
        mask.prop(context.object.hatcher, "draw_mask_5", text = "")
        mask.prop(context.object.hatcher, "draw_mask_6", text = "")
        mask.prop(context.object.hatcher, "draw_mask_7", text = "")
        mask.prop(context.object.hatcher, "draw_mask_8", text = "")

class Light(bpy.types.Panel):
    bl_idname = "LIGHT_PT_Panel"
    bl_label = "Light"
    bl_category = "Panda3DTools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    @classmethod
    def poll(cls, context):
        return (context.active_object is not None and
                context.active_object.type == 'LIGHT' and
                context.selected_objects != [] and
                len(context.selected_objects) <=1)

    def draw(self, context):
        layout = self.layout

        layout.prop(context.object, "name", text='File name')

        if bpy.data.lights[context.selected_objects[0].data.name].type == 'POINT':
            layout.label(text='PointLight')
        if bpy.data.lights[context.selected_objects[0].data.name].type == 'SPOT':
            layout.label(text='SpotLight')
        if bpy.data.lights[context.selected_objects[0].data.name].type == 'SUN':
            layout.label(text='DirectionalLight')

        main = layout.row()
        export_objects = main.row(align = True)
        export_objects.operator("ui.export_object", text="Export light")