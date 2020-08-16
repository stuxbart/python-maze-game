from OpenGL.GL import *
import numpy as np
import settings
from materials import Material

MODEL_TEXTURE_SLOT = 2

MODEL_STATIC = 0
MODEL_DYNAMIC = 1


class VertexBuffer:
    def __init__(self, data, size):
        self.m_renderer_id = glGenBuffers(1)  # VBO
        glBindBuffer(GL_ARRAY_BUFFER, self.m_renderer_id)
        glBufferData(GL_ARRAY_BUFFER, size, data, GL_STATIC_DRAW)

    def destroy(self):
        if settings.DEBUG:
            print(f"Delete vb: {self.m_renderer_id}")
        glDeleteBuffers(1, [self.m_renderer_id])

    def bind(self):
        glBindBuffer(GL_ARRAY_BUFFER, self.m_renderer_id)

    @staticmethod
    def unbind():
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def change_data(self, data, size):
        glBindBuffer(GL_ARRAY_BUFFER, self.m_renderer_id)
        glBufferData(GL_ARRAY_BUFFER, size, data, GL_STATIC_DRAW)


class IndexBuffer:
    def __init__(self, data, count):
        self.m_renderer_id = glGenBuffers(1)  # IBO
        self.m_count = count
        data = np.array(data, dtype=np.int32)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.m_renderer_id)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, data.nbytes, data, GL_STATIC_DRAW)

    def destroy(self):
        if settings.DEBUG:
            print(f"Delete ib: {self.m_renderer_id}")
        glDeleteBuffers(1, [self.m_renderer_id])

    def bind(self):
        glBindBuffer(GL_ARRAY_BUFFER, self.m_renderer_id)

    @staticmethod
    def unbind():
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def get_count(self):
        return self.m_count


class VertexBufferElement:
    def __init__(self, var_type, count, normalized):
        self.var_type = var_type
        self.count = count
        self.normalized = normalized

    def get_size_of_type(self):
        if self.var_type == GL_FLOAT:
            return ctypes.sizeof(GLfloat)
        elif self.var_type == GL_UNSIGNED_INT:
            return ctypes.sizeof(GLuint)
        elif self.var_type == GL_UNSIGNED_BYTE:
            return ctypes.sizeof(GLbyte)
        return 0


class VertexBufferLayout:
    def __init__(self):
        self.m_elements = []
        self.m_stride = 0

    def push_float(self, count):
        self.m_elements.append(VertexBufferElement(GL_FLOAT, count, GL_FALSE))
        self.m_stride += ctypes.sizeof(GLfloat) * count

    def push_u_int(self, count):
        self.m_elements.append(VertexBufferElement(GL_UNSIGNED_INT, count, GL_FALSE))
        self.m_stride += ctypes.sizeof(GLuint) * count

    def push_u_char(self, count):
        self.m_elements.append(VertexBufferElement(GL_UNSIGNED_BYTE, count, GL_TRUE))
        self.m_stride += ctypes.sizeof(GLbyte) * count

    def get_stride(self):
        return self.m_stride

    def get_elements(self):
        return self.m_elements


class VertexArray:
    def __init__(self):
        self.m_renderer_id = glGenVertexArrays(1)  # VAO
        glBindVertexArray(self.m_renderer_id)

    def destroy(self):
        if settings.DEBUG:
            print(f"Delete va: {self.m_renderer_id}")
        glDeleteVertexArrays(1, [self.m_renderer_id])

    def bind(self):
        glBindVertexArray(self.m_renderer_id)

    @staticmethod
    def unbind():
        glBindVertexArray(0)

    def add_buffer(self, vb: VertexBuffer, layout: VertexBufferLayout):
        self.bind()
        vb.bind()
        elements = layout.get_elements()
        offset = 0
        for i, element in enumerate(elements):
            glEnableVertexAttribArray(i)
            glVertexAttribPointer(i, element.count, element.var_type, element.normalized,
                                  layout.get_stride(), ctypes.c_void_p(offset))
            offset += element.count * element.get_size_of_type()


class Vertex:
    def __init__(self, x, y, z, u, v, nx, ny, nz):
        self._vars = np.array([x, y, z, u, v, nx, ny, nz], dtype=np.float32)
        self.x = x
        self.y = y
        self.z = z
        self.u = u
        self.v = v
        self.nx = nx
        self.ny = ny
        self.nz = nz

    def __getitem__(self, item):
        return self._vars[item]

    def __add__(self, other):
        return self._vars + other


class VertexList:
    def __init__(self):
        self._list = []
        self.min_x = 0.0
        self.min_y = 0.0
        self.min_z = 0.0
        self.max_x = 0.0
        self.max_y = 0.0
        self.max_z = 0.0

    def add_vertex(self, vertex):
        if vertex.x < self.min_x:
            self.min_x = vertex.x
        elif vertex.x > self.max_x:
            self.max_x = vertex.x
        elif vertex.y < self.min_y:
            self.min_y = vertex.y
        elif vertex.y > self.max_y:
            self.max_y = vertex.y
        elif vertex.z < self.min_z:
            self.min_z = vertex.z
        elif vertex.z > self.max_z:
            self.max_z = vertex.z
        self._list.append(vertex)

    def get_delta(self, x=0.0, y=0.0, z=0.0):
        delta = np.array([x, y, z, 0.0, 0.0, 0.0, 0.0, 0.0])
        flat_list = []
        for v in self._list:
            flat_list += list((v + delta))
        return np.array(flat_list, dtype=np.float32)

    def count(self):
        return len(self._list)

    def __iter__(self):
        return self._list.__iter__()


class ModelData3D:
    def __init__(self, parent, vertices, texture_coordinates, normals, faces, texture, initialize_gl=False):
        self.parent = parent
        self.texture = texture
        self.vertex_list = VertexList()
        indices = []
        for face in faces:
            for vi, vt, vn in face:
                # Vertex Index/Texture/Normal
                v = Vertex(*vertices[vi], *texture_coordinates[vt], *normals[vn])  # 3 2 3
                self.vertex_list.add_vertex(v)
                indices.append(self.vertex_list.count() - 1)

        indices = np.array(indices, dtype=np.int32)
        self.initialize_gl = initialize_gl
        if self.initialize_gl:
            # Generate Vertex Array Object
            self.va = VertexArray()

            # Generate Vertex Buffer Object
            vertex_lis_flat = self.vertex_list.get_delta(self.position.x, self.position.y, self.position.z)
            self.vb = VertexBuffer(vertex_lis_flat, vertex_lis_flat.nbytes)
            self.layout = VertexBufferLayout()
            self.layout.push_float(3)  # Vertex Position
            self.layout.push_float(2)  # Texture Coordinate
            self.layout.push_float(3)  # Vertex Normal
            # self.layout.push_float(1)  # Vertex Texture
            self.va.add_buffer(self.vb, self.layout)

            # Generate Indices Buffer Object
            self.ib = IndexBuffer(indices, len(indices))

        # update bounding box
        self.bounding_box = SimpleBoundingBox(
            min_x=self.vertex_list.min_x,
            min_y=self.vertex_list.min_y,
            min_z=self.vertex_list.min_z,
            max_x=self.vertex_list.max_x,
            max_y=self.vertex_list.max_y,
            max_z=self.vertex_list.max_z,
        )
        self.position_changed = False

    @property
    def position(self):
        return self.parent.transform

    @property
    def rotation(self):
        return self.parent.rotation

    def destroy(self):
        try:
            self.ib.destroy()
        except AttributeError:
            pass
        try:
            self.vb.destroy()
        except AttributeError:
            pass
        try:
            self.va.destroy()
        except AttributeError:
            pass

    def calculate_vertices_pos(self):
        pass
        # new_pos = self.vertex_list.get_delta(self.position.x, self.position.y, self.position.z)
        # if self.initialize_gl:
        #     self.vb.change_data(new_pos, new_pos.nbytes)

    def rotate(self):
        pass

    def render(self, shader):
        if self.initialize_gl:

            if self.position_changed:
                self.calculate_vertices_pos()
                self.position_changed = False
            pos = np.array([self.position.x, self.position.y, self.position.z, 0.0], dtype=np.float32)
            shader.set_uniform_4fv("DeltaPosition", pos)
            glActiveTexture(GL_TEXTURE0 + MODEL_TEXTURE_SLOT)
            glBindTexture(GL_TEXTURE_2D, self.texture)
            shader.bind()
            shader.set_uniform_1f('TextureIndex', MODEL_TEXTURE_SLOT)
            self.va.bind()
            self.ib.bind()
            glDrawElements(GL_TRIANGLES, self.ib.get_count(), GL_UNSIGNED_INT, None)

        else:
            print("Element is static")


class SimpleBoundingBox:
    def __init__(self, min_x, min_y, min_z, max_x, max_y, max_z):
        self.min_x = min_x
        self.min_y = min_y
        self.min_z = min_z
        self.max_x = max_x
        self.max_y = max_y
        self.max_z = max_z

    @property
    def width(self):
        return self.max_x - self.min_x

    @property
    def height(self):
        return self.max_y - self.min_y

    @property
    def depth(self):
        return self.max_z - self.min_z

    @property
    def x(self):
        return self.min_x + self.width / 2

    @property
    def y(self):
        return self.min_y + self.height / 2

    @property
    def z(self):
        return self.min_z + self.depth / 2

    def update_box(self, min_x=None, min_y=None, min_z=None, max_x=None, max_y=None, max_z=None):
        self.min_x = min_x or self.min_x
        self.min_y = min_y or self.min_y
        self.min_z = min_z or self.min_z
        self.max_x = max_x or self.max_x
        self.max_y = max_y or self.max_y
        self.max_z = max_z or self.max_z


class Model3D:
    def __init__(self, model_name, collision=True, controller=None, model_type=MODEL_STATIC):
        self.name = model_name
        self.visible = True
        self.collision = collision
        self.geometry = None
        self.bounding_box = SimpleBoundingBox(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        self.model_type = model_type

        if model_type == MODEL_STATIC:
            self.controller = None
        elif model_type == MODEL_DYNAMIC:
            self.controller = controller or Controller(self)
        else:
            self.controller = None

        self.transform = ModelTransform(self)
        self.rotation = ModelRotation(self)
        self.material = Material()
        # Physics
        # Tick func
        # static / dynamic

    def destroy(self):
        self.geometry.destroy()

    def position_changed(self):
        if self.geometry:
            self.geometry.position_changed = True
        self.update_bounding_box()

    def rotation_changed(self):
        if self.geometry:
            self.geometry.rotate()

    def set_controller(self, controller):
        self.controller = controller

    def get_controller(self):
        return self.controller

    def render(self, shader):
        if self.visible and self.geometry:

            self.material.bind_material(shader)
            self.geometry.render(shader)

    def set_geometry(self, geometry):
        self.geometry = geometry
        self.update_bounding_box()

    def update_bounding_box(self):
        self.bounding_box.update_box(
            min_x=self.geometry.bounding_box.min_x + self.transform.x,
            min_y=self.geometry.bounding_box.min_y + self.transform.y,
            min_z=self.geometry.bounding_box.min_z + self.transform.z,
            max_x=self.geometry.bounding_box.max_x + self.transform.x,
            max_y=self.geometry.bounding_box.max_y + self.transform.y,
            max_z=self.geometry.bounding_box.max_z + self.transform.z,
        )


class ModelTransform:
    def __init__(self, parent=None, x=0.0, y=0.0, z=0.0):
        self.parent = parent
        self._x = x
        self._y = y
        self._z = z

    def _i_set_x(self, value):
        if value is not None:
            self._x = value
            if isinstance(self.parent, Model3D):
                self.parent.position_changed()

    def _i_get_x(self):
        return self._x

    def _i_set_y(self, value):
        if value is not None:
            self._y = value
            if isinstance(self.parent, Model3D):
                self.parent.position_changed()

    def _i_get_y(self):
        return self._y

    def _i_set_z(self, value):
        if value is not None:
            self._z = value
            if isinstance(self.parent, Model3D):
                self.parent.position_changed()

    def _i_get_z(self):
        return self._z

    y = property(_i_get_y, _i_set_y)
    z = property(_i_get_z, _i_set_z)
    x = property(_i_get_x, _i_set_x)


class ModelRotation:
    def __init__(self, parent, rot_x=0.0, rot_y=0.0, rot_z=0.0):
        self.parent = parent
        self._rot_x = rot_x
        self._rot_y = rot_y
        self._rot_z = rot_z

    def _i_set_rot_x(self, value):
        if value is not None:
            self._rot_x = value
            self.parent.rotation_changed()

    def _i_get_rot_x(self):
        return self._rot_x

    def _i_set_rot_y(self, value):
        if value is not None:
            self._rot_y = value
            self.parent.rotation_changed()

    def _i_get_rot_y(self):
        return self._rot_y

    def _i_set_rot_z(self, value):
        if value is not None:
            self._rot_z = value
            self.parent.rotation_changed()

    def _i_get_rot_z(self):
        return self._rot_z

    rot_x = property(_i_get_rot_x, _i_set_rot_x)
    rot_y = property(_i_get_rot_y, _i_set_rot_y)
    rot_z = property(_i_get_rot_z, _i_set_rot_z)


class Transform:
    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0):
        self.x = x
        self.y = y
        self.z = z

    def get_vec3(self):
        return np.array([self.x, self.y, self.z], dtype=np.float32)

    def get_vec4(self):
        return np.array([self.x, self.y, self.z, 0.0], dtype=np.float32)


class Rotation:
    def __init__(self, rot_x: float = 0.0, rot_y: float = 0.0, rot_z: float = 0.0):
        self.rot_x = rot_x
        self.rot_y = rot_y
        self.rot_z = rot_z


class Controller:
    def __init__(self, parent):
        self.parent = parent
        self.speed_x = 0.0
        self.speed_y = 0.0
        self.speed_z = 0.0

    def show(self):
        self.set_visibility(True)

    def hide(self):
        self.set_visibility(False)

    def set_visibility(self, state: bool):
        self.parent.visible = state

    def set_position(self, x=None, y=None, z=None):
        self.parent.transform.x = x
        self.parent.transform.y = y
        self.parent.transform.z = z

    def move(self, x=0.0, y=0.0, z=0.0):
        if x:
            self.parent.transform.x += x
        if y:
            self.parent.transform.y += y
        if z:
            self.parent.transform.z += z

    def rotate(self, rot_x=None, rot_y=None, rot_z=None):
        self.parent.rotation.rot_x = rot_x
        self.parent.rotation.rot_y = rot_y
        self.parent.rotation.rot_z = rot_z

    def get_position(self):
        return self.parent.transform


class BatchModels:
    def __init__(self, objects: [Model3D]):
        self.vertex_list = VertexList()
        self.texture = None
        self.material = Material()
        indices = []
        for obj in objects:
            if obj.model_type == MODEL_STATIC:
                geometry = obj.geometry
                if isinstance(geometry, ModelData3D):
                    self.texture = geometry.texture
                    vertex_list = geometry.vertex_list
                    for vertex in vertex_list:
                        delta = np.array([obj.transform.x, obj.transform.y, obj.transform.z, 0.0, 0.0, 0.0, 0.0, 0.0])
                        vertex_vars = vertex + delta
                        new_vertex = Vertex(*vertex_vars)
                        self.vertex_list.add_vertex(new_vertex)
                        indices.append(self.vertex_list.count() - 1)

        indices = np.array(indices, dtype=np.int32)

        # Generate Vertex Array Object
        self.va = VertexArray()

        # Generate Vertex Buffer Object
        vertex_lis_flat = self.vertex_list.get_delta(0.0, 0.0, 0.0)
        self.vb = VertexBuffer(vertex_lis_flat, vertex_lis_flat.nbytes)
        self.layout = VertexBufferLayout()
        self.layout.push_float(3)  # Vertex Position
        self.layout.push_float(2)  # Texture Coordinate
        self.layout.push_float(3)  # Vertex Normal
        # self.layout.push_float(1)  # Vertex Texture
        self.va.add_buffer(self.vb, self.layout)

        # Generate Indices Buffer Object
        self.ib = IndexBuffer(indices, len(indices))

    def render(self, shader):
        glActiveTexture(GL_TEXTURE0 + MODEL_TEXTURE_SLOT)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        shader.bind()
        pos = np.array([0.0, 0.0, 0.0, 0.0], dtype=np.float32)
        shader.set_uniform_4fv("DeltaPosition", pos)
        self.material.bind_material(shader)
        shader.set_uniform_1f('TextureIndex', MODEL_TEXTURE_SLOT)
        self.va.bind()
        self.ib.bind()
        glDrawElements(GL_TRIANGLES, self.ib.get_count(), GL_UNSIGNED_INT, None)


if __name__ == "__main__":
    # m = Model3D("elo", True, None, MODEL_STATIC)
    # c = m.get_controller()
    # c.move(y=5)
    v = Vertex(1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0)
    delta = np.array([1, 1, 1, 0.0, 0.0, 0.0, 0.0, 0.0])
    print(v + delta)
