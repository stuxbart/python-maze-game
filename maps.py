from loading_data import load_object
import numpy as np
import settings

from models import BatchModels, MODEL_STATIC, MODEL_DYNAMIC


class Map:
    def __init__(self, file):
        self.map_array = []
        self.objects = []
        self.start_pos = [0, 0, 0]
        self.objective_pos = [0, 0, 0]
        self.main_controller = None
        self.main_character = None
        self.chest = None

        with open(file, 'r') as f:
            for line in f:
                line = line.strip('\n')
                self.map_array.append([x for x in line])
        self.map_array = np.array(self.map_array)
        self.map_array = self.map_array[::-1]
        # print(self.map_array)
        for i, row in enumerate(self.map_array):
            for j, x in enumerate(row):
                position = np.array([j, i, 0.0], dtype=np.float32)
                if x == "#":
                    model = load_object("block", MODEL_STATIC)
                    model.transform.x = j
                    model.transform.y = i
                    self.objects.append(model)
                elif x == " ":
                    model = load_object("ground", MODEL_STATIC)
                    model.collision = False
                    model.transform.x = j
                    model.transform.y = i
                    self.objects.append(model)
                elif x == "/":
                    model = load_object("wall_clock")
                    model.transform.x = j
                    model.transform.y = i
                    self.objects.append(model)
                elif x == "A":
                    self.start_pos = [position[0], position[1], 0]  # Camera Position len(self.map_array) - i - 1
                    # -2, -5
                    model = load_object('character', MODEL_DYNAMIC)

                    c = model.get_controller()
                    c.move(j, i)
                    self.main_controller = c
                    # self.objects.append(model)
                    self.main_character = model

                    model = load_object("ground", MODEL_STATIC)
                    model.collision = False
                    model.transform.x = j
                    model.transform.y = i
                    self.objects.append(model)
                    if settings.DEBUG:
                        print(self.start_pos)
                elif x == "S":
                    self.objective_pos = position

                    model = load_object("ground", MODEL_STATIC)
                    model.collision = False
                    model.transform.x = j
                    model.transform.y = i
                    self.objects.append(model)

                    model = load_object("chest", MODEL_DYNAMIC)
                    model.collision = False
                    model.transform.x = j
                    model.transform.y = i
                    self.objects.append(model)
                    self.chest = model

        self.batch_models = BatchModels(self.objects)

    def check_check_collision(self, dx=0.0, dy=0.0):  # , dz=0.0
        bb1 = self.main_controller.parent.bounding_box
        for obj in self.objects:
            if obj == self.main_controller.parent:
                continue
            if not obj.collision:
                continue
            bb2 = obj.bounding_box
            if bb1.x + dx < bb2.x + bb2.width and bb1.x + dx + bb1.width > bb2.x and\
                    bb1.y + dy < bb2.y + bb2.height and bb1.y + dy + bb1.height > bb2.y:
                if settings.DEBUG:
                    print(f"Collision: {obj} with {self.main_controller.parent}")
                    print(f"{bb1}, {bb2}")
                    print(f"X:{bb1.x, bb2.x}, Y:{bb1.y, bb2.y}")
                return True
        return False

    def destroy(self):
        for i in range(len(self.objects)):
            self.objects[i].destroy()

    def render(self, shader):
        self.batch_models.render(shader)
        # self.main_character.render(shader)
        self.chest.render(shader)
