import numpy as np


class Material:
    def __init__(self):
        white = np.array([1.0, 1.0, 1.0, 1.0], dtype=np.float32)
        black = np.array([0.0, 0.0, 0.0, 1.0], dtype=np.float32)
        var = np.array([50], dtype=np.float32)
        self.emissive = black
        self.diffuse = white
        self.specular = white
        self.shininess = var

    def bind_material(self, shader):
        shader.set_uniform_4fv("MaterialEmissive", self.emissive)
        shader.set_uniform_4fv("MaterialDiffuse", self.diffuse)
        shader.set_uniform_4fv("MaterialSpecular", self.specular)
        shader.set_uniform_1f("MaterialShininess", self.shininess)
