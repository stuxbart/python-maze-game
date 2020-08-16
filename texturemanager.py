from OpenGL.GL import *
import cv2 as cv
import numpy as np
import os


DEFAULT_TEXTURE_SLOT = 0

LOADED_TEXTURES = {}


def load_texture(filepath):
    if filepath in LOADED_TEXTURES:
        return LOADED_TEXTURES[filepath]
    img = load_image_rgba(filepath, flip=True)
    if img is not None:
        width, height = 256, 256
        img = cv.resize(img, (width, height))
        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, width, height,
                     0, GL_RGBA, GL_UNSIGNED_BYTE, img.tostring())

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        # glBindTexture(GL_TEXTURE_2D, 0)
        del img
        LOADED_TEXTURES[filepath] = texture
        return texture
    else:
        return DEFAULT_TEXTURE_SLOT


class TextureManager:
    def __init__(self):
        self.textures = {}
        self._textures = []
        self.n = 0
        self._buffer_index = 0

    def load_texture(self, filepath):
        if filepath in self.textures:
            return self.textures[filepath]
        img = load_image_rgba(filepath, flip=True)
        m_render_id = glGenTextures(1)
        m_local_buffer = img.tostring()
        m_width, m_height, m_BPP = img.shape[0], img.shape[1], 0

        glActiveTexture(GL_TEXTURE0 + self.n)
        glBindTexture(GL_TEXTURE_2D, m_render_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, m_width, m_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, m_local_buffer)
        glBindTexture(GL_TEXTURE_2D, 0)
        del img

        glActiveTexture(GL_TEXTURE0 + self.n)
        glBindTexture(GL_TEXTURE_2D, m_render_id)

        self.textures[filepath] = self.n
        self.n += 1
        return self.n - 1

    def update_texture(self, texture_id, width, height, img):

        glBindTexture(GL_TEXTURE_2D, texture_id+1)
        # glClearTexImage(texture_id, 0, GL_RGBA, GL_UNSIGNED_BYTE, img)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, width, height,
                     0, GL_RGBA, GL_UNSIGNED_BYTE, img)
        glBindTexture(GL_TEXTURE_2D, 0)
        glActiveTexture(GL_TEXTURE0 + texture_id)


class Texture:
    def __init__(self, img):
        self.m_render_id = glGenTextures(1)
        self.m_local_buffer = img.tostring()
        self.m_width, self.m_height, self.m_BPP = img.shape[0], img.shape[1], 0
        glBindTexture(GL_TEXTURE_2D, self.m_render_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, self.m_width, self.m_height,
                     0, GL_RGBA, GL_UNSIGNED_BYTE, self.m_local_buffer)
        glBindTexture(GL_TEXTURE_2D, 0)

    def __del__(self):
        glDeleteTextures(1, self.m_render_id)

    def update(self, new_width=None, new_height=None, img=None):
        if img:
            self.m_local_buffer = img.tostring()
            self.m_width = new_width or img.shape[0] or self.m_width
            self.m_height = new_height or img.shape[1] or self.m_height

            glBindTexture(GL_TEXTURE_2D, self.m_render_id)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, self.m_width, self.m_height,
                         0, GL_RGBA, GL_UNSIGNED_BYTE, None)
            glBindTexture(GL_TEXTURE_2D, 0)
        else:
            print("None textue")

    def bind(self, slot=0):
        glActiveTexture(GL_TEXTURE0 + slot)
        glBindTexture(GL_TEXTURE_2D, self.m_render_id)

    def unbind(self):
        glBindTexture(GL_TEXTURE_2D, 0)

    def get_width(self):
        return self.m_width

    def get_height(self):
        return self.m_height


def load_image_rgba(filepath, flip=False):
    if filepath in IMAGES:
        return IMAGES[filepath]
    if os.path.exists(filepath):
        img = cv.imread(filepath, cv.IMREAD_UNCHANGED)
        if img.shape[2] == 3:
            img = cv.cvtColor(img, cv.COLOR_BGR2RGBA)
        elif img.shape[2] == 4:
            img = cv.cvtColor(img, cv.COLOR_BGRA2RGBA)
        if flip:
            img = cv.flip(img, 0)
        img = np.array(img, dtype=np.uint8)
        IMAGES[filepath] = img
        return img
    else:
        print("Image doesnt exists")
        return None


def load_image_rgba_bytes(*args, **kwargs):
    img = load_image_rgba(*args, **kwargs)
    bytes = img.tostring()
    return bytes


IMAGES = {}

TEXTURES = TextureManager()
