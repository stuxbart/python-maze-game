import numpy as np
from maps import Map
from PySide2.QtCore import Qt
import settings
from camera import Camera


class Game:
    def __init__(self):
        self.client_pos_x, self.client_pos_y, self.client_pos_z = 0.0, 0.0, 0.0  # Camera
        self.camera_speed_forward, self.camera_speed_side, self.camera_speed_z = 0.0, 0.0, 0.0  # Camera
        self.pawn_speed_forward, self.pawn_speed_side, self.pawn_speed_z = 0.0, 0.0, 0.0  # Main Character
        self.moving_forward, self.moving_side = False, False  # Camera / Main Character
        self.current_map = None  # Stay
        self.objective_pos = None  # Stay
        self.character_controller = None  # Stay
        self.cam_with_ctrl = True  # Depends
        self.win_callback = None
        self.ended = False
        self.initialized = False
        self.camera = Camera(None)

    def set_map(self, m="./stages/stage1/mapp.txt"):
        if settings.DEBUG:
            print(self.current_map)
        self.current_map = Map(m)
        self.character_controller = self.current_map.main_controller
        self.camera.set_position(-self.current_map.start_pos[0], -self.current_map.start_pos[1])
        self.client_pos_x = -self.current_map.start_pos[0]
        self.client_pos_y = -self.current_map.start_pos[1]
        self.objective_pos = self.current_map.objective_pos
        self.initialized = True

    def check_win(self):
        if self.initialized:
            transform = self.character_controller.get_position()
            x, y = transform.x, transform.y
            r = np.sqrt((x - self.objective_pos[0]) ** 2 + (y - self.objective_pos[1]) ** 2)
            if r < 1 and not self.ended:
                if settings.DEBUG:
                    print("Win")
                if self.win_callback:
                    self.win_callback()

                self.current_map.destroy()
                self.reset_game_state()

    def reset_game_state(self):
        self.initialized = False
        self.objective_pos = None
        self.character_controller = None
        self.ended = False
        self.current_map = None
        self.camera_speed_forward, self.camera_speed_side = 0.0,0.0

    def set_speed(self, event, mod):
        if self.initialized:
            key = event.text()
            if key == 'w':
                if mod and not self.moving_forward:
                    self.camera_speed_side -= 0.1
                    self.pawn_speed_side += 0.1
                    self.moving_side = True
                else:
                    self.camera_speed_side = 0.0
                    self.pawn_speed_side = 0.0
                    self.moving_side = False
            elif key == 's':
                if mod and not self.moving_forward:
                    self.camera_speed_side += 0.1
                    self.pawn_speed_side -= 0.1
                    self.moving_side = True
                else:
                    self.camera_speed_side = 0.0
                    self.pawn_speed_side = 0.0
                    self.moving_side = False
            elif key == 'a':
                if mod and not self.moving_side:
                    self.camera_speed_forward += 0.1
                    self.pawn_speed_forward -= 0.1
                    self.moving_forward = True
                else:
                    self.camera_speed_forward = 0.0
                    self.pawn_speed_forward = 0.0
                    self.moving_forward = False
            elif key == 'd':
                if mod and not self.moving_side:
                    self.camera_speed_forward -= 0.1
                    self.pawn_speed_forward += 0.1
                    self.moving_forward = True
                else:
                    self.camera_speed_forward = 0.0
                    self.pawn_speed_forward = 0.0
                    self.moving_forward = False

    def lock_camera(self, event):
        if event.key() == Qt.Key_Y:
            self.cam_with_ctrl = not self.cam_with_ctrl

    def move(self, event):
        if self.initialized:
            key = event.text()
            if key == 'w':
                self.client_pos_y -= 0.1
                self.client_pos_x = 0.0
            elif key == 's':
                self.client_pos_y += 0.1
                self.client_pos_x = 0.0
            elif key == 'a':
                self.client_pos_x += 0.1
                self.client_pos_y = 0.0
            elif key == 'd':
                self.client_pos_x -= 0.1
                self.client_pos_y = 0.0

    def move_character(self, event):
        if self.initialized:
            key = event.key()
            if key == Qt.Key_Up and self.cam_with_ctrl:
                if not self.current_map.check_check_collision(dy=0.5):
                    self.character_controller.move(y=0.5)
                    self.client_pos_y -= 0.5
            elif key == Qt.Key_Down and self.cam_with_ctrl:
                if not self.current_map.check_check_collision(dy=-0.5):
                    self.character_controller.move(y=-0.5)
                    self.client_pos_y += 0.5
            elif key == Qt.Key_Left and self.cam_with_ctrl:
                if not self.current_map.check_check_collision(dx=-0.5):
                    self.character_controller.move(x=-0.5)
                    self.client_pos_x += 0.5
            elif key == Qt.Key_Right and self.cam_with_ctrl:
                if not self.current_map.check_check_collision(dx=0.5):
                    self.character_controller.move(x=0.5)
                    self.client_pos_x -= 0.5
            elif key == Qt.Key_Up:
                if not self.current_map.check_check_collision(dy=0.5):
                    self.character_controller.move(y=0.5)
            elif key == Qt.Key_Down:
                if not self.current_map.check_check_collision(dy=-0.5):
                    self.character_controller.move(y=-0.5)
            elif key == Qt.Key_Left:
                if not self.current_map.check_check_collision(dx=-0.5):
                    self.character_controller.move(x=-0.5)
            elif key == Qt.Key_Right:
                if not self.current_map.check_check_collision(dx=0.5):
                    self.character_controller.move(x=0.5)

            pos = self.character_controller.get_position()
            # print(f"Pos, X:{pos.x}, Y:{pos.y}")

    def tick(self):
        if self.initialized:
            self.camera.update()
            self.check_win()
            dx_cam = np.cos(-self.camera.rotation.rot_z) * self.camera_speed_side\
                     + np.sin(self.camera.rotation.rot_z) * self.camera_speed_forward
            dy_cam = np.sin(-self.camera.rotation.rot_z) * self.camera_speed_side\
                     + np.cos(self.camera.rotation.rot_z) * self.camera_speed_forward

            if self.current_map:
                if not self.current_map.check_check_collision(dx=-dy_cam):
                    self.character_controller.move(x=-dy_cam)
                    if self.cam_with_ctrl:
                        self.camera.move(x=dy_cam)
                if not self.current_map.check_check_collision(dy=-dx_cam):
                    self.character_controller.move(y=-dx_cam)
                    if self.cam_with_ctrl:
                        self.camera.move(y=dx_cam)

            self.client_pos_x += self.camera_speed_forward
            self.client_pos_y += self.camera_speed_side
            self.client_pos_z += self.camera_speed_z
