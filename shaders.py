from OpenGL.GL import *
import settings


BASE_SHADERS_FOLDER = "./shaders"


def load_shader_file(path, shader_type):
    full_path = path + shader_type + ".shader"
    with open(full_path, 'r') as f:
        shader = "".join(f)
        return shader


class ShaderSource:
    def __init__(self, path):
        self.vertex_shader = load_shader_file(path, 'vertex_shader')
        self.fragment_shader = load_shader_file(path, 'fragment_shader')


class Shader:
    def __init__(self, shader_name):
        self.m_shader_name = shader_name
        self.source = self.parse_shader(BASE_SHADERS_FOLDER)
        self.m_renderer_id = self.create_shader(self.source.vertex_shader, self.source.fragment_shader)
        self.uniform_locations_cache = {}

    def __del__(self):
        glDeleteProgram(self.m_renderer_id)

    def bind(self):
        glUseProgram(self.m_renderer_id)

    @staticmethod
    def unbind():
        glUseProgram(0)

    def set_uniform_1i(self, uniform_name, value):
        loc = self.get_uniform_location(uniform_name)
        glUniform1i(loc, value)

    def set_uniform_1f(self, uniform_name, value):
        loc = self.get_uniform_location(uniform_name)
        glUniform1f(loc, value)

    def set_uniform_1iv(self, uniform_name, count, value):
        loc = self.get_uniform_location(uniform_name)
        glUniform1iv(loc, count, value)

    def set_uniform_4f(self, uniform_name, v0, v1, v2, v3):
        loc = self.get_uniform_location(uniform_name)
        glUniform4f(loc, v0, v1, v2, v3)

    def set_uniform_4fv(self, uniform_name, vector):
        loc = self.get_uniform_location(uniform_name)
        glUniform4fv(loc, 1, vector)

    def set_uniform_matrix_4fv(self, uniform_name, matrix, count=1, transpose=GL_FALSE):
        loc = self.get_uniform_location(uniform_name)
        glUniformMatrix4fv(loc, count, transpose, matrix)

    def get_uniform_location(self, uniform_name):
        # Do memorize / hash table
        try:
            location = self.uniform_locations_cache[uniform_name]
        except KeyError:
            location = glGetUniformLocation(self.m_renderer_id, uniform_name)
            self.uniform_locations_cache[uniform_name] = location
        if location == -1:

            print(f"Uniform {uniform_name} doesnt exist")
        return location

    def parse_shader(self, filepath):
        return ShaderSource(f"{filepath}/{self.m_shader_name}/")

    @staticmethod
    def compile_shader(shader_type, source):
        shader_id = glCreateShader(shader_type)
        glShaderSource(shader_id, source)
        glCompileShader(shader_id)

        result = glGetShaderiv(shader_id, GL_COMPILE_STATUS)
        if result == GL_FALSE:
            # length = glGetShaderiv(shader_id, GL_INFO_LOG_LENGTH)
            message = glGetShaderInfoLog(shader_id)
            print(f"Failed to compile shader: {message}")
            glDeleteShader(shader_id)
            return 0
        return shader_id

    def create_shader(self, vertex_shader, fragment_shader):
        program = glCreateProgram()
        # Make shades
        vs = self.compile_shader(GL_VERTEX_SHADER, vertex_shader)
        fs = self.compile_shader(GL_FRAGMENT_SHADER, fragment_shader)

        glAttachShader(program, vs)
        glAttachShader(program, fs)
        glLinkProgram(program)
        glValidateProgram(program)

        glDeleteShader(vs)
        glDeleteShader(fs)
        return program
