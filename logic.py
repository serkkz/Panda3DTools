from panda3d.core import Point3, TransformState, LQuaternion
from panda3d.core import Camera, PerspectiveLens, OrthographicLens, CS_default, CS_zup_right, CS_yup_right, CS_zup_left, CS_yup_left, CS_invalid
from panda3d.core import GeomVertexArrayFormat, Geom, GeomVertexFormat, GeomVertexData, GeomVertexWriter, Triangulator3, GeomTriangles
from panda3d.core import GeomNode, PandaNode, NodePath, ModelRoot
from panda3d.core import BamFile, BamWriter, Filename, Notify
from panda3d.core import CollisionPolygon, CollisionNode

import bpy

import bmesh
from mathutils.geometry import distance_point_to_plane

ostream = Notify.out()

list_object_support = {'MESH': False, 'PERSP': False, 'ORTHO': False, 'CAMERA':True}

def show_message_box(message = "", title = "Message Box", icon = 'INFO'):

    def draw(self, context):
        self.layout.label(text = message)

    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)

def checkcreate_dirs(path_project_save):

    # Проверяем существует ли директория, если нет то создаем.
    if not os.path.exists(path_project_save):
        try:
            os.makedirs(path_project_save)
        except OSError as error:
            #print(error)
            pass

def bam_writer_file(path_save, obj):

    file = BamFile()
    file.openWrite(Filename.fromOsSpecific(path_save + '.bam'))

    writer: BamWriter = file.getWriter()
    writer.writeObject(obj)
    writer.flush()

    file.close()

def conversion_transform(obj):

    pos = Point3(obj.location.x, obj.location.y, obj.location.z)
    quat = LQuaternion(obj.rotation_euler.to_quaternion().w, obj.rotation_euler.to_quaternion().x, obj.rotation_euler.to_quaternion().y, obj.rotation_euler.to_quaternion().z)
    scale = Point3(obj.scale.x, obj.scale.y, obj.scale.z)
    transform = TransformState.make_pos_quat_scale(pos, quat, scale)

    return transform

def get_format(obj):

    color = False
    texcoord = False

    # Создаем новый массив.
    geom_vertex_format = GeomVertexArrayFormat()

    # Создаем колонку для вершин.
    geom_vertex_format.add_column("vertex", 3, Geom.NT_float32, Geom.C_point)
    geom_vertex_format.add_column("normal", 3, Geom.NT_float32, Geom.C_normal)

    # Проверка есть ли цвета вершин у объекта.
    if obj.data.vertex_colors.active:
        color = True
        # Создаем колонку для цвета c именем по умолчанию.
        geom_vertex_format.add_column("color", 4, Geom.NT_uint8, Geom.C_color)
        
        # Так же создаем дополнительные колонки.
        for col in obj.data.vertex_colors:
            # Если имя не совподает с активным.
            if not col.name == obj.data.vertex_colors.active.name:
                geom_vertex_format.add_column('color.{}'.format(col.name), 4, Geom.NT_uint8, Geom.C_color)

    # Проверка есть ли активные текстурные координаты у объекта.
    if obj.data.uv_layers.active:
        texcoord = True
        # Создаем колонку для координат c именем по умолчанию.
        geom_vertex_format.add_column("texcoord", 2, Geom.NT_float32, Geom.C_texcoord)
        
        # Так же создаем дополнительные колонки.
        for uv in obj.data.uv_layers:
            # Если имя не совподает с активным.
            if not uv.name == obj.data.uv_layers.active.name:
                geom_vertex_format.add_column('texcoord.{}'.format(uv.name), 2, Geom.NT_float32, Geom.C_texcoord)

    # Создаем формат.
    my_format = GeomVertexFormat()
    my_format.addArray(geom_vertex_format)

    # Регистрируем формат.
    end_format = GeomVertexFormat.registerFormat(my_format)

    return end_format, color, texcoord

def geom_create(obj):

    geom_vertex_format = get_format(obj)

    color  = geom_vertex_format[1]
    texcoord = geom_vertex_format[2]

    vdata = GeomVertexData(obj.data.name, geom_vertex_format[0], Geom.UHStatic)
    vdata.set_num_rows(len(obj.data.vertices))

    vertex_position = GeomVertexWriter(vdata, 'vertex')
    normal_vertex = GeomVertexWriter(vdata, 'normal')

    # Если используются цвета вершин.
    if color:
        color_vertex_list = {'color': GeomVertexWriter(vdata, 'color')}

        # Так же создаем дополнительные слои.
        for col in obj.data.vertex_colors:
            # Если имя не совподает с активным.
            if not col.name == obj.data.vertex_colors.active.name:
                color_vertex_list[col.name] = GeomVertexWriter(vdata, 'color.{}'.format(col.name))

    # Если используются координаты текстур.
    if texcoord:
        texcoord_vertex_list = {'texcoord': GeomVertexWriter(vdata, 'texcoord')}

        # Так же создаем дополнительные слои.
        for uv in obj.data.uv_layers:
            # Если имя не совподает с активным.
            if not uv.name == obj.data.uv_layers.active.name:
                texcoord_vertex_list[uv.name] = GeomVertexWriter(vdata, 'texcoord.{}'.format(uv.name))

    # Запишем порядок треугольников.
    prim = GeomTriangles(Geom.UHStatic)
    prim.makeIndexed()
    prim.setIndexType(Geom.NT_uint32)

    mesh = obj.data
    mesh.calc_loop_triangles()

    # Сюда записиваются индексы обработаных вершин.
    list_vertext = {}

    # Проходим по треугольниуам.
    for triangle in mesh.loop_triangles:

        # Обработка первой вершины.
        if not triangle.loops[0] in list_vertext:

            vertex_position.set_row(triangle.loops[0])
            normal_vertex.set_row(triangle.loops[0])

            vertex_position.add_data3(obj.data.vertices[triangle.vertices[0]].co[0], obj.data.vertices[triangle.vertices[0]].co[1], obj.data.vertices[triangle.vertices[0]].co[2])

            if triangle.use_smooth:
                normal_vertex.add_data3(obj.data.vertices[triangle.vertices[0]].normal[0], obj.data.vertices[triangle.vertices[0]].normal[1], obj.data.vertices[triangle.vertices[0]].normal[2])
            else:
                normal_vertex.add_data3(triangle.normal[0], triangle.normal[1], triangle.normal[2])

            if texcoord:
                for name in texcoord_vertex_list:
                    texcoord_vertex_list[name].set_row(triangle.loops[0])

                    if name == 'texcoord':
                        texcoord_vertex_list[name].addData2(obj.data.uv_layers.active.data[triangle.loops[0]].uv[0], obj.data.uv_layers.active.data[triangle.loops[0]].uv[1])
                    else:
                        texcoord_vertex_list[name].addData2(obj.data.uv_layers[name].data[triangle.loops[0]].uv[0], obj.data.uv_layers[name].data[triangle.loops[0]].uv[1])

            if color:
                for name in color_vertex_list:
                    color_vertex_list[name].set_row(triangle.loops[0])

                    if name == 'color':
                        color_vertex_list[name].addData4(obj.data.vertex_colors.active.data[triangle.loops[0]].color[0],
                                                         obj.data.vertex_colors.active.data[triangle.loops[0]].color[1],
                                                         obj.data.vertex_colors.active.data[triangle.loops[0]].color[2],
                                                         obj.data.vertex_colors.active.data[triangle.loops[0]].color[3])
                    else:
                        color_vertex_list[name].addData4(obj.data.vertex_colors[name].data[triangle.loops[0]].color[0],
                                                         obj.data.vertex_colors[name].data[triangle.loops[0]].color[1],
                                                         obj.data.vertex_colors[name].data[triangle.loops[0]].color[2],
                                                         obj.data.vertex_colors[name].data[triangle.loops[0]].color[3])

            list_vertext[triangle.loops[0]] = None

        # Обработка второй вершины.
        if not triangle.loops[1] in list_vertext:
        
            vertex_position.set_row(triangle.loops[1])
            normal_vertex.set_row(triangle.loops[1])

            vertex_position.add_data3(obj.data.vertices[triangle.vertices[1]].co[0], obj.data.vertices[triangle.vertices[1]].co[1], obj.data.vertices[triangle.vertices[1]].co[2])

            if triangle.use_smooth:
                normal_vertex.add_data3(obj.data.vertices[triangle.vertices[1]].normal[0], obj.data.vertices[triangle.vertices[1]].normal[1], obj.data.vertices[triangle.vertices[1]].normal[2])
            else:
                normal_vertex.add_data3(triangle.normal[0], triangle.normal[1], triangle.normal[2])

            if texcoord:
                for name in texcoord_vertex_list:
                    texcoord_vertex_list[name].set_row(triangle.loops[1])

                    if name == 'texcoord':
                        texcoord_vertex_list[name].addData2(obj.data.uv_layers.active.data[triangle.loops[1]].uv[0], obj.data.uv_layers.active.data[triangle.loops[1]].uv[1])
                    else:
                        texcoord_vertex_list[name].addData2(obj.data.uv_layers[name].data[triangle.loops[1]].uv[0], obj.data.uv_layers[name].data[triangle.loops[1]].uv[1])

            if color:
                for name in color_vertex_list:
                    color_vertex_list[name].set_row(triangle.loops[1])

                    if name == 'color':
                        color_vertex_list[name].addData4(obj.data.vertex_colors.active.data[triangle.loops[1]].color[0],
                                                         obj.data.vertex_colors.active.data[triangle.loops[1]].color[1],
                                                         obj.data.vertex_colors.active.data[triangle.loops[1]].color[2],
                                                         obj.data.vertex_colors.active.data[triangle.loops[1]].color[3])
                    else:
                        color_vertex_list[name].addData4(obj.data.vertex_colors[name].data[triangle.loops[1]].color[0],
                                                         obj.data.vertex_colors[name].data[triangle.loops[1]].color[1],
                                                         obj.data.vertex_colors[name].data[triangle.loops[1]].color[2],
                                                         obj.data.vertex_colors[name].data[triangle.loops[1]].color[3])

            list_vertext[triangle.loops[1]] = None

        # Обработка третьей вершины.
        if not triangle.loops[2] in list_vertext:
        
            vertex_position.set_row(triangle.loops[2])
            normal_vertex.set_row(triangle.loops[2])

            vertex_position.add_data3(obj.data.vertices[triangle.vertices[2]].co[0], obj.data.vertices[triangle.vertices[2]].co[1], obj.data.vertices[triangle.vertices[2]].co[2])
            
            if triangle.use_smooth:
                normal_vertex.add_data3(obj.data.vertices[triangle.vertices[2]].normal[0], obj.data.vertices[triangle.vertices[2]].normal[1], obj.data.vertices[triangle.vertices[2]].normal[2])
            else:
                normal_vertex.add_data3(triangle.normal[0], triangle.normal[1], triangle.normal[2])

            if texcoord:
                for name in texcoord_vertex_list:
                    texcoord_vertex_list[name].set_row(triangle.loops[2])

                    if name == 'texcoord':
                        texcoord_vertex_list[name].addData2(obj.data.uv_layers.active.data[triangle.loops[2]].uv[0], obj.data.uv_layers.active.data[triangle.loops[2]].uv[1])
                    else:
                        texcoord_vertex_list[name].addData2(obj.data.uv_layers[name].data[triangle.loops[2]].uv[0], obj.data.uv_layers[name].data[triangle.loops[2]].uv[1])

            if color:
                for name in color_vertex_list:
                    color_vertex_list[name].set_row(triangle.loops[2])

                    if name == 'color':
                        color_vertex_list[name].addData4(obj.data.vertex_colors.active.data[triangle.loops[2]].color[0],
                                                         obj.data.vertex_colors.active.data[triangle.loops[2]].color[1],
                                                         obj.data.vertex_colors.active.data[triangle.loops[2]].color[2],
                                                         obj.data.vertex_colors.active.data[triangle.loops[2]].color[3])
                    else:
                        color_vertex_list[name].addData4(obj.data.vertex_colors[name].data[triangle.loops[2]].color[0],
                                                         obj.data.vertex_colors[name].data[triangle.loops[2]].color[1],
                                                         obj.data.vertex_colors[name].data[triangle.loops[2]].color[2],
                                                         obj.data.vertex_colors[name].data[triangle.loops[2]].color[3])

            list_vertext[triangle.loops[2]] = None

        # Добавляем вершины в примитив.
        prim.addVertices(triangle.loops[0], triangle.loops[1], triangle.loops[2])

    prim.closePrimitive()

    geom = Geom(vdata)
    geom.addPrimitive(prim)

    return geom
 
def get_quad(obj):
    print("get_quad")

def check_coplanar(obj, poly):

    v1 = obj.data.vertices[poly.vertices[1]].co - obj.data.vertices[poly.vertices[0]].co
    v2 = obj.data.vertices[poly.vertices[2]].co - obj.data.vertices[poly.vertices[0]].co

    for index in poly.vertices[3:]:
        if abs(distance_point_to_plane(obj.data.vertices[index].co, obj.data.vertices[poly.vertices[0]].co, v1.cross(v2))) < 1e-6:
            return True
        else:
            return False

def get_coplanar(obj):

    #coplanar = []
    not_coplanar = []

    # Перебираем полигоны.
    for poly in obj.data.polygons:
        # Если вершины три, это значит полигон автоматически копланарен.
        #if len(poly.vertices) == 3:
            #coplanar.append(poly)

        if not check_coplanar(obj, poly):
            not_coplanar.append(poly)

    for i in obj.data.vertices:
        i.select=False
        if i.co.x > 0:
            i.select = True
    for i in obj.data.edges:
        i.select=False
    for i in obj.data.polygons:
        i.select = False

    #for f in coplanar: print(f.index)
    for poly in not_coplanar: 
        poly.select = True

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_mode(type="FACE")


def triangle_poly(poly, obj):

    trangle = {}

    triangulator3 = Triangulator3()

    index_tr = 0
    
    for index in poly.vertices:
        triangulator3.add_polygon_vertex(index_tr)
        triangulator3.add_vertex(*obj.data.vertices[index].co)
        
        index_tr += 1

    triangulator3.triangulate()

    for i in range(triangulator3.getNumTriangles()):
        v0 = triangulator3.get_vertex(triangulator3.get_triangle_v0(i))
        v1 = triangulator3.get_vertex(triangulator3.get_triangle_v1(i))
        v2 = triangulator3.get_vertex(triangulator3.get_triangle_v2(i))

        #collision_node.add_solid(CollisionPolygon((v0[0], v0[1], v0[2]), (v1[0], v1[1], v1[2]), (v2[0], v2[1], v2[2])))

        trangle[i] = ((v0[0], v0[1], v0[2]), (v1[0], v1[1], v1[2]), (v2[0], v2[1], v2[2]))

    return trangle

def add_polygons_to_dict(dict_named, poly, obj):
    # Если нет такого ключа в словаре.
    if not obj.data.materials[poly.material_index].name in dict_named:
        # Дабавляем ключ и список.
        dict_named[obj.data.materials[poly.material_index].name] = [poly]
    else:
        # Если есть такой ключ, добавляем к списку.
        dict_named[obj.data.materials[poly.material_index].name].append(poly)

def collision_polygon_create(obj, scene):

    named_triangles = {}
    named_coplanar = {}
    named_not_coplanar = {}
    named_not_quad = {}

    triangles = []
    coplanar = []
    not_coplanar = []
    not_quad = []

    # Перебираем полигоны объекта чтоб извлечь полигоны.
    for poly in obj.data.polygons:
    
        # Если есть материал.
        if len(obj.data.materials) >> 0:

            mat = True

            # Если полигон из трех вершин, проверка на компланарность не нужна.
            if len(poly.vertices) == 3:
                for index in poly.vertices[2:]:
                    add_polygons_to_dict(named_triangles, poly, obj)

            # Если у полигона четыре вершины, необходимо проверить на компланарность.
            elif len(poly.vertices) == 4:
                # Если полигон компланарный
                if check_coplanar(obj, poly):
                    add_polygons_to_dict(named_coplanar, poly, obj)
                else:
                    add_polygons_to_dict(named_not_coplanar, poly, obj)

            # Если у полигона более четырех вершин, необходимо разбить на треугольники.
            elif len(poly.vertices) >= 4:
                add_polygons_to_dict(named_not_quad, poly, obj)

        # Если нет материала.
        else:

            mat = False

            # Если полигон из трех вершин, проверка на компланарность не нужна.
            if len(poly.vertices) == 3:
                for index in poly.vertices[2:]:
                    triangles.append(poly)

            # Если у полигона четыре вершины, необходимо проверить на компланарность.
            elif len(poly.vertices) == 4:
                if check_coplanar(obj, poly):
                    coplanar.append(poly)
                else:
                    not_coplanar.append(poly)

            # Если у полигона более четырех вершин, необходимо разбить на треугольники.
            elif len(poly.vertices) >= 4:
                not_quad.append(poly)


    # Если есть материал.
    if mat:

        group = NodePath(obj.name)

        collision_node_dict = {}

        # Создаем полигоны столкновения из треугольников.
        for name in named_triangles:
            # Создаем CollisionNode
            collision_node = CollisionNode(name)
            for poly in named_triangles[name]:
                vertext_quad = []
                for index in poly.vertices:
                    vertext_quad.append(Point3(*obj.data.vertices[index].co))
                quad = CollisionPolygon(vertext_quad[0], vertext_quad[1], vertext_quad[2])
                collision_node.add_solid(quad)
                vertext_quad = []

            collision_node_dict[name] = collision_node


        # Создаем полигоны столкновения из треугольников.
        for name in named_coplanar:

            # Создаем CollisionNode
            collision_node = CollisionNode(name)
            
            for poly in named_coplanar[name]:
                vertext_quad = []
                for index in poly.vertices:
                    vertext_quad.append(Point3(*obj.data.vertices[index].co))

                quad = CollisionPolygon(vertext_quad[0], vertext_quad[1], vertext_quad[2], vertext_quad[3])

                if name in collision_node_dict:
                    collision_node_dict[name].add_solid(quad)
                else:
                    collision_node.add_solid(quad)
                    collision_node_dict[name] = collision_node

                vertext_quad = []

        #print(collision_node_dict)


                
        # Создаем полигоны столкновения из треугольников.
        for name in named_not_coplanar:
        
            # Создаем CollisionNode
            collision_node = CollisionNode(name)

            # Нужно разбить некомпланарные полигоны, на треугольники.
            for poly in named_not_coplanar[name]:
                for vertext in triangle_poly(poly, obj).values():
                    quad = CollisionPolygon(vertext[0], vertext[1], vertext[2])

                    if name in collision_node_dict:
                        collision_node_dict[name].add_solid(quad)
                    else:
                        collision_node.add_solid(quad)
                        collision_node_dict[name] = collision_node


        # Создаем полигоны столкновения из треугольников.
        for name in named_not_quad:
        
            # Создаем CollisionNode
            collision_node = CollisionNode(name)

            # Нужно разбить некомпланарные полигоны, на треугольники.
            for poly in named_not_quad[name]:
                for vertext in triangle_poly(poly, obj).values():
                    quad = CollisionPolygon(vertext[0], vertext[1], vertext[2])

                    if name in collision_node_dict:
                        collision_node_dict[name].add_solid(quad)
                    else:
                        collision_node.add_solid(quad)
                        collision_node_dict[name] = collision_node


        for col in collision_node_dict.values():
            node_path = NodePath(col)
            node_path.reparentTo(group)
            node_path.show()


        return group

    # Если нет материала.
    else:

        collision_node = CollisionNode(obj.name)

        vertext_quad = []

        # Создаем полигоны столкновения из четырех угольников.
        for poly in coplanar:
            for index in poly.vertices:
                vertext_quad.append(Point3(*obj.data.vertices[index].co))
            quad = CollisionPolygon(vertext_quad[0], vertext_quad[1], vertext_quad[2], vertext_quad[3])
            collision_node.add_solid(quad)
            vertext_quad = []

        # Создаем полигоны столкновения из треугольников.
        for poly in triangles:
            for index in poly.vertices:
                vertext_quad.append(Point3(*obj.data.vertices[index].co))
            quad = CollisionPolygon(vertext_quad[0], vertext_quad[1], vertext_quad[2])
            collision_node.add_solid(quad)
            vertext_quad = []

        # Нужно разбить некомпланарные полигоны, на треугольники.
        for poly in not_coplanar:
            triangle_poly(collision_node, poly, obj)

        # Нужно разбить полигоны у которых более четырех сторон на треугольники.
        for poly in not_quad:
            triangle_poly(collision_node, poly, obj)

        node_path = NodePath(collision_node)
        node_path.show()

        return node_path

def geom_node_create(obj, scene):

    geom = geom_create(obj)
    
    geom_node = GeomNode(obj.data.name)
    geom_node.addGeom(geom)

    return geom_node

def camera_create(obj, scene):

    frame_size = obj.data.view_frame(scene = scene)

    if obj.data.type == 'PERSP':
        lens = PerspectiveLens()

    if obj.data.type == 'ORTHO':
        lens = OrthographicLens()
        
    lens.set_film_size(abs(frame_size[0][0]) + abs(frame_size[1][0]), abs(frame_size[0][1]) + abs(frame_size[1][1]))
    lens.set_focal_length(abs(frame_size[0][2]))
    lens.set_near_far(obj.data.clip_start, obj.data.clip_end)
    
    if obj.hatcher.coordinate_system == "CS_default":
        lens.set_coordinate_system(CS_default)
    if obj.hatcher.coordinate_system == "CS_zup_right":
        lens.set_coordinate_system(CS_zup_right)
    if obj.hatcher.coordinate_system == "CS_yup_right":
        lens.set_coordinate_system(CS_yup_right)
    if obj.hatcher.coordinate_system == "CS_zup_left":
        lens.set_coordinate_system(CS_zup_left)
    if obj.hatcher.coordinate_system == "CS_yup_left":
        lens.set_coordinate_system(CS_yup_left)
    if obj.hatcher.coordinate_system == "CS_invalid":
        lens.set_coordinate_system(CS_invalid)
        
    camera = Camera(obj.data.name)
    camera.active = obj.hatcher.camera_active
    
    bit = '{}{}{}{}{}{}{}{}'.format(obj.hatcher.draw_mask_1.decode('utf-8'), obj.hatcher.draw_mask_2.decode('utf-8'), obj.hatcher.draw_mask_3.decode('utf-8'), obj.hatcher.draw_mask_4.decode('utf-8'), 
                                    obj.hatcher.draw_mask_5.decode('utf-8'), obj.hatcher.draw_mask_6.decode('utf-8'), obj.hatcher.draw_mask_7.decode('utf-8'), obj.hatcher.draw_mask_8.decode('utf-8'))

    camera.camera_mask = int(bit, 2)
    camera.set_lens(lens)

    return camera

def build_hierarchy(obj, scene):
    # Узел для формирование иерархии
    root = NodePath("root")

    # Выполним рекурсию, для поиска всех.
    def recurse(obj, parent):
        # Переменая которая содережит функцию необходимую для экспорта данного типа объекта.
        create_object = None

        # Если объект является сеткой.
        if obj.type == "MESH":
            if obj.hatcher.type_mesh == "Render":
                create_object = geom_node_create

            if obj.hatcher.type_mesh == "Collision":
                create_object = collision_polygon_create

        # Если объект является источником цвета.
        if obj.type == "LIGHT":
            create_object = "LIGHT"

        # Если объект является камерой.
        if obj.type == "CAMERA":
            if obj.data.type != 'PANO':
                create_object = camera_create

        # Если есть родитель.
        if not parent:
            npp = NodePath(create_object(obj, scene))
            npp.setName(obj.name)
            #npp.show()
            npp.reparentTo(root)
            npp.set_transform(root, conversion_transform(obj))

        else:
            # Если нет родителя.
            np = NodePath(create_object(obj, scene))
            np.setName(obj.name)
            #np.show()
            np.set_transform(conversion_transform(obj))

            # Проверяем есть ли такой объект в иерархии.
            result = root.find('**/{}'.format(parent.name))

            if result:
                np.reparentTo(result)
                np.set_transform(root, conversion_transform(obj))
            else:
                np.reparentTo(root)
                np.set_transform(root, conversion_transform(obj))

        # Проходим по детям.
        for child in obj.children:
            recurse(child, obj)

    recurse(obj, obj.parent)

    return root.node().getChild(0)

import os
from datetime import datetime

class ExportObject(bpy.types.Operator):
    bl_idname = "ui.export_object"
    bl_label = "Generator_object"

    def execute(self, context):
        start_time = datetime.now()

        # Перебираем список выбранных объектов.
        for obj in context.selected_objects:
            # Объединяем путь проекта и относительную директорию модели.
            path_project_save = os.path.join(context.scene.hatcher.ful_path_project, obj.hatcher.rel_path_object)

            # Проверяем существует ли директория, если нет то создаем.
            checkcreate_dirs(path_project_save)

            # Объединяем путь директории и имя файла.
            path_save = os.path.join(path_project_save, obj.name)
            
            node = build_hierarchy(obj, context.scene)
            root = ModelRoot('{}.bam'.format(obj.name))
            root.add_child(node)

            bam_writer_file(path_save, root)

            show_message_box('Export object: {} completed, time: {}'.format(obj.name, datetime.now() - start_time), "Message")

        return {'FINISHED'}

class ExportScene(bpy.types.Operator):
    bl_idname = "ui.export_scene"
    bl_label = "Generator_scene"

    def execute(self, context):
        start_time = datetime.now()

        # Объединяем путь проекта и относительную директорию сцены.
        path_project_save = os.path.join(context.scene.hatcher.ful_path_project, context.scene.hatcher.rel_path_scene)
        
        # Проверяем существует ли директория, если нет то создаем.
        checkcreate_dirs(path_project_save)

        # Создаем корень для объединения.
        root = ModelRoot('{}.bam'.format(context.scene.name))

        # Пройдем по всем объектом в сцене.
        for obj in context.scene.objects:
            # Нас интересуют объекты только без родителя.
            if not obj.parent:
                # Проверим есть ли данный тип объекта среди поддерживаемых.
                if obj.type in list_object_support:
                    # Если есть ли подтип.
                    if list_object_support[obj.type]:
                        if not obj.data.type == 'PANO':
                            node = build_hierarchy(obj, context.scene)
                            root.add_child(node)
                    else:
                        node = build_hierarchy(obj, context.scene)
                        root.add_child(node)

                # Объединяем путь директории и имя сцены.
                path_save = os.path.join(path_project_save, context.scene.name)

                bam_writer_file(path_save, root)

        show_message_box('Export scene, completed, time: {}'.format(datetime.now() - start_time), "Message")

        return {'FINISHED'}

class ExportSelected(bpy.types.Operator):
    bl_idname = "ui.export_selected"
    bl_label = "Generator_selected"

    def execute(self, context):
        start_time = datetime.now()

        # Объединяем путь проекта и относительную директорию сцены.
        path_project_save = os.path.join(context.scene.hatcher.ful_path_project, context.scene.hatcher.rel_path_other)

        # Проверяем существует ли директория, если нет то создаем.
        checkcreate_dirs(path_project_save)

        # Если поле имени файла заполнено, то объеденяем в один файл.
        if not context.scene.hatcher.file_name_selected == '':

            # Создаем корень для объединения.
            root = ModelRoot('{}.bam'.format(context.scene.hatcher.file_name_selected))

            # Перебираем список выбранных объектов.
            for obj in context.selected_objects:
                # Проверим есть ли данный тип объекта среди поддерживаемых.
                if obj.type in list_object_support:
                    # Если есть ли подтип.
                    if list_object_support[obj.type]:
                        if not obj.data.type == 'PANO':
                            node = build_hierarchy(obj, context.scene)
                            root.add_child(node)
                    else:
                        node = build_hierarchy(obj, context.scene)
                        root.add_child(node)

            # Объединяем путь директории и имя файла.
            path_save = os.path.join(path_project_save, context.scene.hatcher.file_name_selected)

            bam_writer_file(path_save, root)

        # Если нет, то раздельно.
        else:
            # Перебираем список выбранных объектов.
            for obj in context.selected_objects:
            
                # Проверим есть ли данный тип объекта среди поддерживаемых.
                if obj.type in list_object_support:
                    # Если есть ли подтип.
                    if list_object_support[obj.type]:
                        if not obj.data.type == 'PANO':
                            node = build_hierarchy(obj, context.scene)
                            # Объединяем путь директории и имя файла.
                            path_save = os.path.join(path_project_save, obj.name)
                            bam_writer_file(path_save, node)
                    else:
                        node = build_hierarchy(obj, context.scene)
                        # Объединяем путь директории и имя файла.
                        path_save = os.path.join(path_project_save, obj.name)
                        bam_writer_file(path_save, node)

        show_message_box('Export selected, completed, time: {}'.format(datetime.now() - start_time), "Message")

        return {'FINISHED'}

class CheckingCoplanarity(bpy.types.Operator):
    bl_idname = "ui.check_coplanarity"
    bl_label = "Checking_coplanarity"

    def execute(self, context):

        get_coplanar(context.object)

        return {'FINISHED'}

class CheckingQuad(bpy.types.Operator):
    bl_idname = "ui.check_quad"
    bl_label = "Checking_quad"
    
    def execute(self, context):
    
        get_quad(context.object)
        
        return {'FINISHED'}
