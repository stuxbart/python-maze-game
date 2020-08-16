from models import Transform, Rotation
from shaders import Shader
import numpy as np
from pyrr import matrix44, Vector3, Vector4


class Camera:
    def __init__(self, shader):
        self.transform = Transform(0.0, 0.0, -7.0)
        self.target_transform = Transform()
        self.rotation = Rotation(90 / 180 * np.pi, 0.0, 90 / 180 * np.pi)  # 70 / 360 * np.pi, 0.0, -40 / 360 * np.pi)
        self.shader = shader
        self.screen_width = 0.0
        self.screen_height = 0.0

        self.view_angle = 70.0

        self.clip_range_min = 0.1
        self.clip_range_max = 100.0

        if not self.shader:
            self.setup_shader()

        self.light_position_w = Vector4([2.0, 2.0, 0.5, 0.0])
        self.ambient = [1.0, 0.1, 0.1, 1.0]

    @property
    def aspect_ratio(self):
        if self.screen_width and self.screen_height:
            return self.screen_width / self.screen_height
        else:
            return 4/3

    def setup_shader(self):
        self.shader = Shader("advanced_shader")
        samplers = np.array([x for x in range(8)], dtype=np.uint32)
        self.shader.bind()
        self.shader.set_uniform_1iv('u_Textures', len(samplers), samplers)

    def set_ambient(self, ambient=(0.1, 0.1, 0.1, 1.0)):
        self.shader.bind()
        self.ambient = ambient
        ambient = np.array(ambient, dtype=np.float32)
        self.shader.set_uniform_4fv("Ambient", ambient)

    def update_mvp(self):
        self.shader.bind()
        proj = matrix44.create_perspective_projection_matrix(self.view_angle, self.aspect_ratio,
                                                             self.clip_range_min, self.clip_range_max)
        view = matrix44.create_from_translation(Vector3([self.transform.x, self.transform.y, self.transform.z]))
        model = matrix44.create_from_translation(Vector3([0.0, 0.0, 0.0]))
        rotation = matrix44.create_from_x_rotation(self.rotation.rot_x)  # 70 / 360 * np.pi
        rot_z_mat = matrix44.create_from_z_rotation(self.rotation.rot_z)  # -40 / 360 * np.pi
        rotation = matrix44.multiply(rot_z_mat, rotation)
        rp = matrix44.multiply(rotation, proj)
        vrp = matrix44.multiply(view, rp)
        mvp = matrix44.multiply(model, vrp)

        self.shader.set_uniform_matrix_4fv("ModelViewProjectionMatrix", mvp)

    def update_camera_pos(self):
        self.shader.bind()
        self.shader.set_uniform_4fv("EyePosW", Vector4([self.transform.x, self.transform.y, self.transform.z, 0.0]))

    def set_model_matrix(self):
        self.shader.bind()
        rotation = matrix44.create_from_x_rotation(self.rotation.rot_x)
        rot_z_mat = matrix44.create_from_z_rotation(self.rotation.rot_z)
        rotation = matrix44.multiply(rot_z_mat, rotation)

        self.shader.set_uniform_matrix_4fv("ModelMatrix", rotation)

    def update(self):
        self.shader.bind()
        model_matrix = matrix44.create_from_translation(Vector3([3.0, 3.0, 2.0]))
        self.shader.set_uniform_4fv("LightPosW", self.light_position_w)  # Light
        white = np.array([1.0, 1.0, 1.0, 1.0], dtype=np.float32)  # Light
        self.shader.set_uniform_4fv("LightColor", white)  # Light
        self.set_ambient([0.6, 0.6, 0.6, 1.0])

        self.update_mvp()
        self.set_model_matrix()
        self.update_camera_pos()

    def resize(self, w, h):
        self.screen_width = w
        self.screen_height = h

    def move(self, x=0.0, y=0.0, z=0.0):
        if x:
            self.transform.x += x
        if y:
            self.transform.y += y
        if z:
            self.transform.z += z

    def set_position(self, x=0.0, y=0.0, z=-0.3):
        self.transform.x = x
        self.transform.y = y
        self.transform.z = z
