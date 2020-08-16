from OpenGL.GL import *
from OpenGL.GL import shaders
from shaders import *
from pyrr import matrix44, Vector3, Matrix44, Vector4
import numpy as np
from PySide2.QtCore import Qt
from PySide2.QtGui import QCursor

from texturemanager import load_image_rgba
from shaders import Shader
from renderer import Renderer
from game import Game
from hud import Scene, ImageLayer, GUI, SNAP_LEFT_DOWN, Button
from camera import Camera
import settings


class OpenGLController:
    def __init__(self, widget):
        self.opengl_widget = widget
        self.basic_shader = None
        self.advanced_shader = None
        self.shader_hud = None
        self.shader_text = None
        self.renderer = None
        self.camera = None
        self.game = None
        self.gui = None
        self.start_scene = None
        self.exit_scene = None
        self.game_scene = None
        self.level_scene = None
        self.win_scene = None
        self.esc_scene = None

        self.mouse_pos_x = 0.0
        self.mouse_pos_y = 0.0

    def make_main_menu(self):
        self.start_scene = Scene(1200, 600)
        self.gui.add_scene('main', self.start_scene)
        self.gui.activate_scene('main')

        img = load_image_rgba('./graphics/hud/main_menu.png', True)
        main_image_layer = ImageLayer(1200, 600, 0, 0, img, True, resizable=True)
        self.start_scene.add_layer(main_image_layer, SNAP_LEFT_DOWN)

        button_red_image = load_image_rgba('./graphics/hud/button_n_red.png', True)
        button_red = Button(400, 100, 400, 50, button_red_image, 'Exit')
        self.start_scene.add_layer(button_red)
        button_red.connect(self.show_exit_menu)

        button_green_image = load_image_rgba('./graphics/hud/button_n_blue.png', True)
        button_green1 = Button(400, 100, 400, 200, button_green_image, 'Options')
        self.start_scene.add_layer(button_green1)

        button_green2 = Button(400, 100, 400, 350, button_green_image, 'StartGame')
        self.start_scene.add_layer(button_green2)
        button_green2.connect(self.start_game)

    def make_exit_menu(self):
        self.exit_scene = Scene(1200, 600)
        self.gui.add_scene('exit', self.exit_scene)

        exit_menu_bg_img = load_image_rgba('./graphics/hud/exit_menu.png', True)
        exit_menu_bg = ImageLayer(1200, 600, 0, 0, exit_menu_bg_img, True, resizable=True)
        self.exit_scene.add_layer(exit_menu_bg, SNAP_LEFT_DOWN)

        button_red_image = load_image_rgba('./graphics/hud/button_n_red.png', True)
        exit_red_button = Button(400, 100, 700, 300, button_red_image, 'Exit')
        self.exit_scene.add_layer(exit_red_button)
        exit_red_button.connect(self.close_game)

        button_green_image = load_image_rgba('./graphics/hud/button_n_green.png', True)
        exit_green_button = Button(400, 100, 100, 300, button_green_image, 'Cancel')
        self.exit_scene.add_layer(exit_green_button)
        exit_green_button.connect(self.back_to_main_menu)

    def make_esc_menu(self):
        self.esc_scene = Scene(1200, 600)
        self.gui.add_scene('esc', self.esc_scene)

        exit_menu_bg_img = load_image_rgba('./graphics/hud/exit_menu.png', True)
        exit_menu_bg = ImageLayer(1200, 600, 0, 0, exit_menu_bg_img, True, resizable=True)
        self.esc_scene.add_layer(exit_menu_bg, SNAP_LEFT_DOWN)

        button_red_image = load_image_rgba('./graphics/hud/button_n_red.png', True)
        exit_red_button = Button(400, 100, 400, 100, button_red_image, 'Exit')
        self.esc_scene.add_layer(exit_red_button)
        exit_red_button.connect(self.close_game)

        button_green_image = load_image_rgba('./graphics/hud/button_n_green.png', True)
        main_manu_button = Button(400, 100, 400, 300, button_green_image, 'MainMenu')
        self.esc_scene.add_layer(main_manu_button)
        main_manu_button.connect(self.back_to_main_menu)

        button_blue_image = load_image_rgba('./graphics/hud/button_n_blue.png', True)
        cancel_button = Button(400, 100, 400, 500, button_blue_image, 'Cancel')
        self.esc_scene.add_layer(cancel_button)
        cancel_button.connect(lambda: self.change_scene('game'))

    def make_level_menu(self):
        self.level_scene = Scene(1200, 600)
        self.gui.add_scene('levels', self.level_scene)
        # self.gui.activate_scene('levels')

        level_menu_bg_img = load_image_rgba('./graphics/hud/select_level_menu.png', True)
        level_menu_bg = ImageLayer(1200, 600, 0, 0, level_menu_bg_img, True, resizable=True)
        self.level_scene.add_layer(level_menu_bg, SNAP_LEFT_DOWN)

        lev1_button_img = load_image_rgba('./graphics/hud/level_button.png', True)
        # for i, folder in enumerate(os.listdir('./stages')):
        #     for j, file in enumerate(os.listdir(f'./stages/{folder}')):
        #         path = f"./stages/{folder}/{file}"
        #         level_name = file.split('.')[0]
        #         lev1_button = Button(300, 300, 300 * (1+j), 300 * i, lev1_button_img, level_name)
        #         new_path = path
        #         l = lambda: print(new_path)
        #         lev1_button.connect(l)
        #         self.level_scene.add_layer(lev1_button)
        #         print(path)
        lev1_button = Button(300, 300, 300, 300, lev1_button_img, "Mapp")
        lev1_button.connect(lambda: self.select_map("./stages/stage1/mapp.txt"))
        self.level_scene.add_layer(lev1_button)

        lev2_button = Button(300, 300, 600, 300, lev1_button_img, "Mapa")
        lev2_button.connect(lambda: self.select_map("./stages/stage1/mapa.txt"))
        self.level_scene.add_layer(lev2_button)

    def make_game_scene(self):
        self.game_scene = Scene(1200, 600)
        self.gui.add_scene('game', self.game_scene)

        button_green_image = load_image_rgba('./graphics/hud/button_n_blue.png', True)
        game_back_button = Button(150, 50, 5, 550, button_green_image, 'b')
        self.game_scene.add_layer(game_back_button)
        game_back_button.connect(self.back_to_main_menu)

    def make_win_scene(self):
        self.win_scene = Scene(1200, 600)
        self.gui.add_scene('win', self.win_scene)

        win_scene_bg_img = load_image_rgba('./graphics/hud/win_screen.png', True)
        win_scene_bg = ImageLayer(1200, 600, 0, 0, win_scene_bg_img, True, resizable=True)
        self.win_scene.add_layer(win_scene_bg, SNAP_LEFT_DOWN)

        button_green_image = load_image_rgba('./graphics/hud/button_green.png', True)
        next_level_button = Button(250, 100, 800, 100, button_green_image, 'Next')
        self.win_scene.add_layer(next_level_button)
        next_level_button.connect(self.back_to_main_menu)

        back_main_menu_btn = Button(350, 100, 100, 100, button_green_image, 'MainMenu')
        self.win_scene.add_layer(back_main_menu_btn)
        back_main_menu_btn.connect(self.back_to_main_menu)

    def init(self):
        """Initialize GL widget, set viewport, compile shader"""
        self.basic_shader = Shader('basic_shader')
        self.shader_hud = Shader("hud_shader")
        self.shader_text = Shader("text_shader")
        self.advanced_shader = Shader("advanced_shader")

        self.basic_shader.bind()
        self.renderer = Renderer()
        # self.camera = Camera(self.advanced_shader)

        self.game = Game()
        self.game.win_callback = self.show_win_scene
        self.opengl_widget.game = self.game

        self.gui = GUI()
        self.make_main_menu()
        self.make_exit_menu()
        self.make_game_scene()
        self.make_level_menu()
        self.make_win_scene()
        self.make_esc_menu()

        glEnable(GL_DEPTH_TEST)
        # self.set_viewpoint()

        glClearColor(0.2, 0.2, 0.5, 1)

        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_BLEND)

        # block_text = load_texture("./graphics/textures/wall_block.png")
        # hud_text = load_texture("./graphics/hud/hud.png")
        #
        # glActiveTexture(GL_TEXTURE0)
        # glBindTexture(GL_TEXTURE_2D, block_text)
        # glActiveTexture(GL_TEXTURE1)
        # glBindTexture(GL_TEXTURE_2D, hud_text)

        # sampler_array_lock = self.shader.get_uniform_location('u_Textures')
        samplers = np.array([x for x in range(8)], dtype=np.uint32)
        # glUniform1iv(sampler_array_lock, 3, samplers)
        self.basic_shader.bind()
        self.basic_shader.set_uniform_1iv('u_Textures', len(samplers), samplers)

        self.shader_hud.bind()
        self.shader_hud.set_uniform_1iv('u_Textures', len(samplers), samplers)

        self.shader_text.bind()
        self.shader_text.set_uniform_1iv('u_Textures', len(samplers), samplers)

        self.advanced_shader.bind()
        self.advanced_shader.set_uniform_1iv('u_Textures', len(samplers), samplers)

    def draw(self):
        """Called every frame"""
        self.renderer.clear()
        self.game.tick()
        # self.set_viewpoint()

        # self.camera.update()
        try:
            if self.game.initialized:
                self.game.current_map.render(self.game.camera.shader)
            self.gui.render(self.shader_hud, self.shader_text)
        except AttributeError as e:
            print("Shader not initialized: ", e)

    def widget_resized(self, w, h):
        glViewport(0, 0, w, h)
        self.shader_hud.bind()
        self.gui.resize(w, h)
        self.shader_hud.set_uniform_matrix_4fv('u_VP', self.start_scene.ortho_matrix)
        self.shader_text.bind()
        self.shader_text.set_uniform_matrix_4fv('projection', self.start_scene.ortho_matrix)
        self.game.camera.resize(w, h)

    def set_advanced_variables(self):
        self.advanced_shader.bind()
        model_matrix = matrix44.create_from_translation(Vector3([3.0, 3.0, 2.0]))
        self.advanced_shader.set_uniform_4fv("LightPosW", Vector4([2.0, 2.0, 0.5, 0.0]))
        white = np.array([1.0, 1.0, 1.0, 1.0], dtype=np.float32)
        self.advanced_shader.set_uniform_4fv("LightColor", white)
        ambient = np.array([0.1, 0.1, 0.1, 1.0], dtype=np.float32)
        self.advanced_shader.set_uniform_4fv("Ambient", ambient)

        proj = matrix44.create_perspective_projection_matrix(45.0, self.opengl_widget.aspect_ratio, 0.1, 100.0)
        view = matrix44.create_from_translation(Vector3([self.game.client_pos_x, self.game.client_pos_y, -7.0]))
        model = matrix44.create_from_translation(Vector3([0.0, 0.0, 0.0]))
        rotation = matrix44.create_from_x_rotation(70 / 360 * np.pi)
        rot_z_mat = matrix44.create_from_z_rotation(-40 / 360 * np.pi)
        rotation = matrix44.multiply(rot_z_mat, rotation)
        rp = matrix44.multiply(rotation, proj)
        vrp = matrix44.multiply(view, rp)
        mvp = matrix44.multiply(model, vrp)

        self.advanced_shader.set_uniform_matrix_4fv("ModelViewProjectionMatrix", mvp)
        self.advanced_shader.set_uniform_matrix_4fv("ModelMatrix", rotation)
        self.advanced_shader.set_uniform_4fv("EyePosW", Vector4([self.game.client_pos_x, self.game.client_pos_y, -7.0, 0.0]))

        black = np.array([0.0, 0.0, 0.0, 1.0], dtype=np.float32)
        self.advanced_shader.set_uniform_4fv("MaterialEmissive", black)
        self.advanced_shader.set_uniform_4fv("MaterialDiffuse", white)
        self.advanced_shader.set_uniform_4fv("MaterialSpecular", white)
        var = np.array([50], dtype=np.float32)
        self.advanced_shader.set_uniform_1f("MaterialShininess", var)

    def set_viewpoint(self):
        """Calculate viewpoint based on zoom, aspect ratio, view angle, clipping"""
        proj = matrix44.create_perspective_projection_matrix(45.0, self.opengl_widget.aspect_ratio, 0.1, 100.0)
        view = matrix44.create_from_translation(Vector3([self.game.client_pos_x, self.game.client_pos_y, -7.0]))
        model = matrix44.create_from_translation(Vector3([0.0, 0.0, 0.0]))
        rotation = matrix44.create_from_x_rotation(70 / 360 * np.pi)
        rot_z_mat = matrix44.create_from_z_rotation(-40 / 360 * np.pi)
        rotation = matrix44.multiply(rot_z_mat, rotation)
        rp = matrix44.multiply(rotation, proj)
        vrp = matrix44.multiply(view, rp)
        mvp = matrix44.multiply(model, vrp)
        self.basic_shader.bind()
        self.basic_shader.set_uniform_matrix_4fv('u_MVP', mvp)

    def set_camera_rotation(self, rot_x=0.0, rot_y=0.0, rot_z=0.0):
        rot_x_mat = Matrix44.from_x_rotation(rot_x)
        rot_y_mat = Matrix44.from_y_rotation(rot_y)
        rot_z_mat = Matrix44.from_z_rotation(rot_z)
        rotation_matrix = matrix44.multiply(rot_z_mat, rot_x_mat)
        self.basic_shader.set_uniform_matrix_4fv("rotation", rotation_matrix)

    def mouse_move(self, pos_x, pos_y):

        self.gui.mouse_move(pos_x, pos_y)

    def clicked(self, pos_x, pos_y):
        self.gui.clicked(pos_x, pos_y)

    def start_game(self):
        self.gui.activate_scene('levels')

    def show_exit_menu(self):
        self.gui.activate_scene('exit')

    def close_game(self):
        self.opengl_widget.parent.close()

    def back_to_main_menu(self):
        self.gui.activate_scene('main')

    def select_map(self, map_name):
        if settings.DEBUG:
            print(map_name)
        self.game.set_map(map_name)
        self.gui.activate_scene('game')

    def change_scene(self, scene):
        self.gui.activate_scene(scene)

    def show_win_scene(self):
        self.gui.activate_scene('win')

    def show_esc_menu(self):
        self.gui.activate_scene('esc')

    def rotate_camera(self, event):
        pos_x, pos_y = event.localPos().x(), event.localPos().y()
        dx = pos_x - self.mouse_pos_x
        dy = pos_y - self.mouse_pos_y
        self.mouse_pos_x = pos_x
        self.mouse_pos_y = pos_y

        if event.buttons() == Qt.MiddleButton:
            if self.game.initialized:
                self.game.camera.rotation.rot_z -= dx * 0.01
                self.game.camera.rotation.rot_x -= dy * 0.01
                # QCursor.setPos(self.gui.width / 2, self.gui.height / 2)
