import sys
from PySide2.QtWidgets import QApplication, QMainWindow
from PySide2.QtCore import QTimer, Qt
from PySide2.QtOpenGL import QGLWidget
from opengl import OpenGLController


class OpenGLWidget(QGLWidget):
    def __init__(self, parent):
        self.parent = parent
        QGLWidget.__init__(self)
        self.controller = OpenGLController(self)
        self.grabKeyboard()
        self.setMouseTracking(True)
        self.game = None

    @property
    def aspect_ratio(self):
        """:return Widget aspect ratio"""
        rect = self.geometry()
        return rect.width() / rect.height()

    def initializeGL(self):
        """Initialize GL widget, set viewport, compile shader"""
        self.controller.init()

    def paintGL(self):
        """Called every frame"""
        self.controller.draw()

    def resizeGL(self, w: int, h: int):
        """Called when widget is resized"""
        self.controller.widget_resized(w, h)

    def keyPressEvent(self, event):
        self.game.set_speed(event, mod=True)
        self.game.move_character(event)
        self.game.lock_camera(event)
        if event.key() == Qt.Key_Escape:
            self.controller.show_esc_menu()

    def keyReleaseEvent(self, event):

        self.game.set_speed(event, mod=False)

    def mouseMoveEvent(self, event):
        self.controller.mouse_move(event.localPos().x(), event.localPos().y())

        self.controller.rotate_camera(event)

    def mousePressEvent(self, event):

        x, y = event.localPos().x(), event.localPos().y()
        self.controller.clicked(x, y)


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.resize(1200, 700)
        self.main_widget = OpenGLWidget(self)
        self.setCentralWidget(self.main_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    fps = 140
    opengl_widget_loop = QTimer()
    opengl_widget_loop.timeout.connect(window.main_widget.update)
    opengl_widget_loop.start(int(1000 / fps))
    sys.exit(app.exec_())
