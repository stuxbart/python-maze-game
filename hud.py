import numpy as np
import cv2 as cv
import string
from OpenGL.GL import *
from pyrr import matrix44
from models import VertexArray, VertexBuffer, VertexBufferLayout, IndexBuffer
from texturemanager import TEXTURES, load_image_rgba

SNAP_CENTER = 0
SNAP_LEFT_DOWN = 1
SNAP_RIGHT_DOWN = 2
SNAP_RIGHT_TOP = 3
SNAP_LEFT_TOP = 4

TEXT_TEXTURE_SLOT = 3
MENU_TEXTURE_SLOT = 4


class Character:
    def __init__(self, char, texture_id, size, bearing, advance):
        self.char = char
        self.texture_id = texture_id
        self.size = size
        self.bearing = bearing
        self.advance = advance


CHARACTERS = []


def init_character(scale=2):
    for l in string.ascii_letters:
        size = cv.getTextSize(l, cv.FONT_HERSHEY_SIMPLEX, scale, 3)
        s = {'width': size[0][0], 'height': size[0][1]}
        empty = np.ones((s['height'] + scale, s['width'], 4), dtype=np.uint8)
        cv.putText(empty, l, (0, s['height'] - scale), cv.FONT_HERSHEY_SIMPLEX, scale,
                   (250, 250, 250, 255), 3, 8)
        img = cv.resize(empty, (64, 64))
        img = cv.flip(img, 0)
        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, 64, 64,
                     0, GL_RGBA, GL_UNSIGNED_BYTE, img.tostring())

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        c = Character(l, texture, (s['width'], s['height']), (0, 0), empty.shape[0])
        CHARACTERS.append(c)
        # print(f"Character: {l}, {string.ascii_letters.index(l)}")


class VLayout:
    def __init__(self, x, y, max_h, offset):
        self.items = []
        self.x = x
        self.y = y
        self.offset = offset
        self.max_h = max_h

    def add_item(self, item):
        self.items.append(item)
        self.calculate_positions()

    def calculate_positions(self):
        dy = 0
        for i in self.items:
            i.move(self.x, self.y+dy)
            dy += i.height
            dy += self.offset

    def move(self, new_x, new_y):
        self.x = new_x or self.x
        self.y = new_y or self.y
        self.calculate_positions()


class HLayout:
    def __init__(self, x, y, max_w, offset):
        self.items = []
        self.x = x
        self.y = y
        self.offset = offset
        self.max_w = max_w

    def add_item(self, item):
        self.items.append(item)
        self.calculate_positions()

    def calculate_positions(self):
        dx = 0
        for i in self.items:
            i.move(self.x+dx, self.y)
            dx += i.width
            dx += self.offset

    def move(self, new_x, new_y):
        self.x = new_x or self.x
        self.y = new_y or self.y
        self.calculate_positions()


class TextLayer:
    def __init__(self, x, y, scale, text, color, resizable=False):
        self.width = 0
        self.height = 0
        self.x = x
        self.y = y
        self.scale = scale
        self.text = text
        self.color = color
        self.visible = True
        self.resizable = resizable
        if not CHARACTERS:
            init_character()

        vertices = np.array([
            10.0, 10.0, 0.0, 0.0,
            200, 10, 1.0, 0.0,
            200, 200, 1.0, 1.0,
            10, 200, 0.0, 1.0,
        ], dtype=np.float32)
        indices = np.array([
            0, 1, 2, 2, 3, 0
        ], dtype=np.uint32)
        self.va = VertexArray()
        self.vb = VertexBuffer(vertices, vertices.nbytes)
        layout = VertexBufferLayout()
        layout.push_float(2)  # Vertex Position
        layout.push_float(2)  # Texture Coordinate
        self.va.add_buffer(self.vb, layout)

        self.ib = IndexBuffer(indices, len(indices))

    def render_text(self, shader):
        glActiveTexture(GL_TEXTURE0 + TEXT_TEXTURE_SLOT)
        m = 0
        for l in self.text:
            character = CHARACTERS[string.ascii_letters.index(l)]
            x_pos = self.x + m + character.bearing[0] * self.scale
            y_pos = self.y + character.bearing[1] * self.scale
            w = character.size[0] * self.scale
            h = character.size[1] * self.scale

            m += character.size[0] * self.scale  # character advance

            vertices = np.array([
                x_pos, y_pos, 0.0, 0.0,
                x_pos + w, y_pos, 1.0, 0.0,
                x_pos + w, y_pos + h, 1.0, 1.0,
                x_pos, y_pos + h, 0.0, 1.0,
            ], dtype=np.float32)
            indices = np.array([
                0, 1, 2, 2, 3, 0
            ], dtype=np.uint32)

            glBindTexture(GL_TEXTURE_2D, character.texture_id)
            # glBindVertexArray(self.vao)
            # glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
            # glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
            # glBindBuffer(GL_ARRAY_BUFFER, 0)
            # glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ibo)
            # glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)
            # glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
            self.vb.change_data(vertices, vertices.nbytes)

            glDisable(GL_DEPTH_TEST)
            shader.bind()
            self.va.bind()
            self.ib.bind()
            glDrawElements(GL_TRIANGLES, self.ib.get_count(), GL_UNSIGNED_INT, None)
            glEnable(GL_DEPTH_TEST)

    def render(self, shader):
        self.render_text(shader)

    def set_text(self, new_text):
        self.text = new_text

    def hide(self):
        self.visible = False

    def show(self):
        self.visible = True

    def move(self, new_x, new_y):
        self.x = new_x
        self.y = new_y

    def resize(self, w, h):
        pass


class ImageLayer:
    def __init__(self, w, h, x, y, img, full_screen=False, resizable=False):
        self.width = w
        self.height = h
        self.x = x
        self.y = y
        self.visible = True
        self.resizable = resizable
        self.full_screen = full_screen
        self.img = img
        self.img = cv.resize(self.img, (self.width, self.height))

        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, self.width, self.height,
                     0, GL_RGBA, GL_UNSIGNED_BYTE, self.img.tostring())

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        vertices = np.array([
            self.x, self.y, 0.0, 0.0, 4.0,
            self.x + self.width, self.y, 1.0, 0.0, 4.0,
            self.x + self.width, self.y + self.height, 1.0, 1.0, 4.0,
            self.x, self.y + self.height, 0.0, 1.0, 4.0,
        ], dtype=np.float32)
        indices = np.array([
            0, 1, 2, 2, 3, 0
        ], dtype=np.uint32)
        self.va = VertexArray()
        self.vb = VertexBuffer(vertices, vertices.nbytes)
        layout = VertexBufferLayout()
        layout.push_float(2)  # Vertex Position
        layout.push_float(2)  # Texture Coordinate
        layout.push_float(1)  # Texture Index
        self.va.add_buffer(self.vb, layout)
        self.ib = IndexBuffer(indices, len(indices))

    def calculate_vertices(self):
        vertices = np.array([
            self.x, self.y, 0.0, 0.0, 4.0,
            self.x + self.width, self.y, 1.0, 0.0, 4.0,
            self.x + self.width, self.y + self.height, 1.0, 1.0, 4.0,
            self.x, self.y + self.height, 0.0, 1.0, 4.0,
        ], dtype=np.float32)
        self.vb.change_data(vertices, vertices.nbytes)

    def render(self, shader):
        glActiveTexture(GL_TEXTURE0 + MENU_TEXTURE_SLOT)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glDisable(GL_DEPTH_TEST)
        shader.bind()
        self.va.bind()
        self.ib.bind()
        glDrawElements(GL_TRIANGLES, self.ib.get_count(), GL_UNSIGNED_INT, None)
        glEnable(GL_DEPTH_TEST)

    def set_img(self, img):
        # compare img size with layer size
        self.img = img
        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, self.width, self.height,
                     0, GL_RGBA, GL_UNSIGNED_BYTE, img.tostring())

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

    def hide(self):
        self.visible = False

    def show(self):
        self.visible = True

    def move(self, new_x, new_y):
        self.x = new_x or self.x
        self.y = new_y or self.y
        self.calculate_vertices()

    def resize(self, new_width=None, new_height=None):
        self.width = new_width or self.width
        self.height = new_height or self.height
        self.calculate_vertices()


class Button:
    def __init__(self, w, h, x, y, img, text='', text_color=(255, 255, 255, 255), resizable=False):
        self.width = w
        self.height = h
        self.x = x
        self.y = y
        self.callback = None
        self.visible = True
        self.resizable = resizable
        self.img = img
        self.text = text
        self.color = text_color
        self._image_item = ImageLayer(w, h, x, y, img)
        hov_img = cv.subtract(img, 50)
        self._hover_image_item = ImageLayer(w, h, x, y, hov_img)
        self.hover = True

        text_x, text_y = self._text_pos()
        self._text_item = TextLayer(text_x, text_y, 1, text, text_color)

    def _text_pos(self):
        delta_x = 0
        delta_y = 0
        for l in self.text:
            if not CHARACTERS:
                init_character()
            x, y = CHARACTERS[string.ascii_letters.index(l)].size
            delta_x += x
            if y > delta_y:
                delta_y = y
        text_pos_x = self.x + self.width / 2 - delta_x / 2
        text_pos_y = self.y + self.height / 2 - delta_y / 2
        return text_pos_x, text_pos_y

    def set_hover(self, state):
        self.hover = state

    def render(self, main_shader, text_shader):
        if self.hover:
            self._hover_image_item.render(main_shader)
        else:
            self._image_item.render(main_shader)
        self._text_item.render(text_shader)

    def move(self, new_x, new_y):
        self.x = new_x or self.x
        self.y = new_y or self.y
        self._image_item.move(new_x, new_y)
        self._hover_image_item.move(new_x, new_y)
        text_x, text_y = self._text_pos()
        self._text_item.move(text_x, text_y)

    def resize(self, new_width=None, new_height=None):
        self.width = new_width or self.width
        self.height = new_height or self.height

    def clicked(self):
        if self.callback:
            self.callback()

    def connect(self, callback):
        self.callback = callback


class Scene:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.layers = {}
        self.ortho_matrix = None
        self.calculate_matrix()

    def get_orthogonal_matrix(self):
        return self.ortho_matrix

    def calculate_matrix(self):
        self.ortho_matrix = matrix44.create_orthogonal_projection_matrix(0.0, self.width, 0.0, self.height, 0.0, 1.0)

    def resize(self, width, height):
        self.width = width
        self.height = height
        self.calculate_matrix()
        for l, desc in self.layers.items():
            new_x = self.width * self.layers[l]['x'] - self.layers[l]['delta_x']
            new_y = self.height * self.layers[l]['y'] - self.layers[l]['delta_y']
            l.move(new_x, new_y)
            if l.resizable:
                l.resize(width, height)

    def render(self, main_shader, text_shader):
        for l, desc in self.layers.items():
            if l.visible:
                if isinstance(l, TextLayer):
                    l.render(text_shader)
                elif isinstance(l, ImageLayer):
                    l.render(main_shader)
                elif isinstance(l, Button):
                    l.render(main_shader, text_shader)

    def add_layer(self, layer, snap_point=SNAP_CENTER):
        if isinstance(layer, ImageLayer):
            if layer.full_screen:
                layer.resize(self.width, self.height)
        if snap_point == SNAP_CENTER:
            delta_x = layer.width / 2
            delta_y = layer.height / 2
        elif snap_point == SNAP_LEFT_DOWN:
            delta_x = 0
            delta_y = 0
        elif snap_point == SNAP_RIGHT_DOWN:
            delta_x = layer.width
            delta_y = 0
        elif snap_point == SNAP_RIGHT_TOP:
            delta_x = layer.width
            delta_y = layer.height
        elif snap_point == SNAP_LEFT_TOP:
            delta_x = 0
            delta_y = layer.height
        else:
            print("Invalid snap point")  # set snap to center
            delta_x = layer.width / 2
            delta_y = layer.height / 2

        self.layers[layer] = {
            'width': layer.width / self.width,
            'height': layer.height / self.height,
            'x': (layer.x + delta_x) / self.width,
            'y': (layer.y + delta_y) / self.height,
            'delta_x': delta_x,
            'delta_y': delta_y,
        }

    def mouse_move(self, x, y):
        y = self.height - y
        for l, desc in self.layers.items():
            if l.visible:
                if isinstance(l, Button):
                    if l.x < x < l.x + l.width and l.y < y < l.y + l.height:
                        l.set_hover(True)
                    else:
                        l.set_hover(False)

    def clicked(self, x, y):
        y = self.height - y

        for l, desc in self.layers.items():
            if l.visible:
                if isinstance(l, Button):
                    if l.x < x < l.x + l.width and l.y < y < l.y + l.height:
                        l.clicked()
                        break
    # Layers Order
    # static / dynamic
    # resizable / non resizable


class GUI:
    def __init__(self):
        self.scenes = {}
        self.active_scene = None
        self.width = 0.0
        self.height = 0.0

    def add_scene(self, name, scene):
        self.scenes[name] = scene

    def activate_scene(self, name):
        if name in self.scenes:
            self.active_scene = self.scenes[name]

    def render(self, main_shader, text_shader):
        self.active_scene.render(main_shader, text_shader)

    def mouse_move(self, x, y):
        self.active_scene.mouse_move(x, y)

    def clicked(self, x, y):
        self.active_scene.clicked(x, y)

    def resize(self, w, h):
        self.width = w
        self.height = h
        for scene_name, scene in self.scenes.items():
            scene.resize(w, h)


if __name__ == "__main__":
    text = TextLayer(10, 10, 2, 'l', (10, 10, 10))
