from OpenGL.GL import *


class Renderer:
    @staticmethod
    def draw(va, ib, shader):
        shader.bind()
        va.bind()
        ib.bind()
        glDrawElements(GL_TRIANGLES, ib.get_count(), GL_UNSIGNED_INT, None)

    @staticmethod
    def draw_hud(va, ib, shader):
        glDisable(GL_DEPTH_TEST)
        shader.bind()
        va.bind()
        ib.bind()
        glDrawElements(GL_TRIANGLES, ib.get_count(), GL_UNSIGNED_INT, None)
        glEnable(GL_DEPTH_TEST)

    @staticmethod
    def clear():
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
