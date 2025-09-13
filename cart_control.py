import sys
import math
import numpy as np
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QSlider
)
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from OpenGL.GL import *
from OpenGL.GLU import *

class OpenGLWidget(QOpenGLWidget):
    """
    Класс-отрисовщик ("холст"). Изменений не требует.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.wheel_radius: float = 0.06
        self.axle_length: float = 0.4
        self.masts_lenght: float = 0.3
        self.world_points: dict = {}

    def initializeGL(self):
        glClearColor(0.1, 0.1, 0.2, 1.0)
        glEnable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)

    def resizeGL(self, w: int, h: int):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        aspect_ratio = w / h if h > 0 else 1
        if w >= h:
            glOrtho(-1.0 * aspect_ratio, 1.0 * aspect_ratio, -1.0, 1.0, -1.0, 1.0)
        else:
            glOrtho(-1.0, 1.0, -1.0 / aspect_ratio, 1.0 / aspect_ratio, -1.0, 1.0)
        glViewport(0, 0, w, h)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0.0, -0.5, 0.0)

        if not self.world_points:
            return

        glColor3f(0.9, 0.9, 0.9)
        glLineWidth(2.0)
        
        p1 = self.world_points['point_a']
        p2 = self.world_points['point_b']
        p3 = self.world_points.get('point_c')
        p4_array = self.world_points.get('points_d')
        wl = self.world_points['wheel_left']
        wr = self.world_points['wheel_right']

        vec = np.array([0, -self.wheel_radius, 0])
        glBegin(GL_LINES)

        glVertex2f(wl[0]-0.1, wl[1])
        glVertex2f(wr[0]+0.1, wr[1])

        glVertex2f(p1[0], p1[1])
        glVertex2f(p2[0], p2[1])

        glVertex2f(p2[0], p2[1])
        glVertex2f(p3[0], p3[1])

        p4_attach = p4_array[0] # Точка крепления
        p4_L_top = p4_array[1]    # Левый верхний угол
        p4_L_bot = p4_array[2]    # Левый нижний
        p4_R_top = p4_array[3]    # Правый верхний
        p4_R_bot = p4_array[4]    # Правый нижний
        
        # Соединяем C с основанием захвата D
        glVertex2f(p3[0], p3[1])
        glVertex2f(p4_attach[0], p4_attach[1])
        
        # Рисуем сам захват
        glVertex2f(p4_L_top[0], p4_L_top[1]) # Перекладина
        glVertex2f(p4_R_top[0], p4_R_top[1])
        glVertex2f(p4_L_top[0], p4_L_top[1]) # Левый "палец"
        glVertex2f(p4_L_bot[0], p4_L_bot[1])
        glVertex2f(p4_R_top[0], p4_R_top[1]) # Правый "палец"
        glVertex2f(p4_R_bot[0], p4_R_bot[1])
        
        glEnd()
        
        self._draw_circle(self.wheel_radius, center=wl+vec)
        self._draw_circle(self.wheel_radius, center=wr+vec)

        glColor3f(1.0, 0.2, 0.2)
        self._draw_point(center=p1)
        self._draw_point(center=p2)
        self._draw_point(center=p3)
        self._draw_point(center=p4_attach)

        glFlush()

    def _draw_circle(self, radius, center, segments=100):
        glBegin(GL_LINE_LOOP)
        for i in range(segments):
            angle = 2.0 * math.pi * i / segments
            glVertex2f(center[0] + radius * math.cos(angle), 
                       center[1] + radius * math.sin(angle))
        glEnd()

    def _draw_point(self, center, radius=0.02, segments=16):
        glBegin(GL_TRIANGLE_FAN)
        glVertex2f(center[0], center[1])
        for i in range(segments + 1):
            angle = 2.0 * math.pi * i / segments
            glVertex2f(center[0] + radius * math.cos(angle), 
                       center[1] + radius * math.sin(angle))
        glEnd()

    def update_geometry(self, points: dict):
        self.world_points = points
        self.update()

class MainWindow(QMainWindow):
    """
    Главное окно приложения ("мозг").
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Управление тележкой (Платформа на y=0)")
        self.setGeometry(100, 100, 900, 600)

        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        coord_font = QFont("Consolas", 12)
        self.coord_label1 = QLabel(font=coord_font)
        self.coord_label2 = QLabel(font=coord_font)
        self.coord_label3 = QLabel(font=coord_font) 
        self.coord_label4 = QLabel(font=coord_font)
        self.opengl_widget = OpenGLWidget()
        left_layout.addWidget(self.coord_label1)
        left_layout.addWidget(self.coord_label2)
        left_layout.addWidget(self.coord_label3) 
        left_layout.addWidget(self.coord_label4) 
        left_layout.addWidget(self.opengl_widget, 1)

        right_panel = QWidget()
        right_panel.setFixedWidth(200)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
 
        self.slider_a = QSlider(Qt.Orientation.Horizontal, minimum=-200, maximum=200)
        self.slider_a_value_label = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)

        self.slider_b = QSlider(Qt.Orientation.Horizontal, minimum=40, maximum=100)
        self.slider_b_value_label = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)

        self.slider_c = QSlider(Qt.Orientation.Horizontal, minimum=0, maximum=180)
        self.slider_c_value_label = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)

        self.slider_d = QSlider(Qt.Orientation.Horizontal, minimum=0, maximum=360)
        self.slider_d_value_label = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)

        self.slider_e = QSlider(Qt.Orientation.Horizontal, minimum=40, maximum=100)
        self.slider_e_value_label = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)

        right_layout.addWidget(QLabel("<b>Параметр 'a' (Смещение X)</b>"))
        right_layout.addWidget(self.slider_a)
        right_layout.addWidget(self.slider_a_value_label)
        right_layout.addSpacing(20)

        right_layout.addWidget(QLabel("<b>Параметр 'b' (Высота мачты)</b>"))
        right_layout.addWidget(self.slider_b)
        right_layout.addWidget(self.slider_b_value_label)
        right_layout.addSpacing(20)

        right_layout.addWidget(QLabel("<b>Параметр 'c' (Угол поворота)</b>"))
        right_layout.addWidget(self.slider_c)
        right_layout.addWidget(self.slider_c_value_label)
        right_layout.addSpacing(20)

        right_layout.addWidget(QLabel("<b>Параметр 'd' (Угол поворота)</b>"))
        right_layout.addWidget(self.slider_d)
        right_layout.addWidget(self.slider_d_value_label)
        right_layout.addSpacing(20)

        right_layout.addWidget(QLabel("<b>Параметр 'e' (Высота мачты)</b>"))
        right_layout.addWidget(self.slider_e)
        right_layout.addWidget(self.slider_e_value_label)
        right_layout.addSpacing(20)

        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 0)

        self.slider_a.valueChanged.connect(self.update_system)
        self.slider_b.valueChanged.connect(self.update_system)
        self.slider_c.valueChanged.connect(self.update_system)
        self.slider_d.valueChanged.connect(self.update_system)
        self.slider_e.valueChanged.connect(self.update_system)

        self.slider_a.setValue(0)
        self.slider_b.setValue(60)
        self.slider_c.setValue(45)
        self.slider_d.setValue(45)
        self.slider_e.setValue(60)

        self.update_system()

    def update_system(self):
        """ Главный метод вычислений. Вызывается при движении любого ползунка. """
        param_a = self.slider_a.value() / 200.0
        param_b = self.slider_b.value() / 200.0
        angle_deg_c = self.slider_c.value()
        param_c = np.deg2rad(angle_deg_c)
        angle_deg_d = self.slider_d.value()
        param_d = np.deg2rad(angle_deg_d)
        param_e = self.slider_e.value() / 200.0
        
        # --- ИЗМЕНЕНИЕ ЗДЕСЬ: Локальные координаты теперь отсчитываются от центра оси ---
        axle_length = self.opengl_widget.axle_length
        masts_lenght = self.opengl_widget.masts_lenght
        local_vectors = {
            'point_a':      np.array([0, 0, 1]),
            'point_b':      np.array([0, 0, 1]), # Точка B - это просто начало координат, смещенное своей матрицей
            'point_c':      np.array([masts_lenght, 0, 1]), # Вектор длины мачты C
            # 'point_d':     np.array([0, -param_e, 1]),
            'points_d':     np.array([[0, -param_e, 1],
                                      [-0.05, -param_e, 1],
                                      [-0.05, -param_e-0.05, 1],
                                      [0.05, -param_e, 1],
                                      [0.05, -param_e-0.05, 1]]),

            'wheel_left':   np.array([-axle_length/2, 0, 1]),
            'wheel_right':  np.array([axle_length/2, 0, 1])
        }
        
        transformation_matrices = { 'point_a' :  np.array([ [1., 0., param_a],
                                                            [0., 1., 0],
                                                            [0., 0., 1]]),
                                    'point_b' :  np.array([ [1., 0., 0.],
                                                            [0., 1., param_b],
                                                            [0., 0., 1.]]),
                                    'point_c' :  np.array([ [np.cos(param_c),   -np.sin(param_c),   0.],
                                                            [np.sin(param_c),   np.cos(param_c),    0.],
                                                            [0.,                 0.,                  1.]]),
                                    'points_d' :  np.array([ [np.cos(param_d),   -np.sin(param_d),   0.],
                                                            [np.sin(param_d),   np.cos(param_d),    0.],
                                                            [0.,                 0.,                  1.]])}
        

        value_matrix =  np.array([[1., 0., 0.],
                        [0., 1., 0.],
                        [0., 0., 1.]])
        
        value_vector = np.array([0., 0., 1.])
        res_trans_matrices = dict()
        world_points = {'wheel_left': np.array([-axle_length / 2 + param_a, 0, 1]),
                        'wheel_right':np.array([ axle_length / 2 + param_a, 0, 1])}
        for name, matr in transformation_matrices.items():
            if name in local_vectors and name != 'points_d':

                world_points[name] = matr @ local_vectors[name] + value_vector
                value_vector = world_points[name]

                print(value_matrix)
            if name == 'points_d':
                world_points['points_d'] = (matr @ local_vectors[name].T).T + value_vector
        

        
        self.opengl_widget.update_geometry(world_points)
        
        self.slider_a_value_label.setText(f"{param_a:.2f}")
        self.slider_b_value_label.setText(f"{param_b:.2f}")
        self.slider_c_value_label.setText(f"{angle_deg_c}°")
        self.slider_d_value_label.setText(f"{angle_deg_d}°")
        self.slider_e_value_label.setText(f"{param_e:.2f}°")

        p1 = world_points['point_a']
        p2 = world_points['point_b']
        p3 = world_points['point_c']
        p4 = world_points['points_d']

        self.coord_label1.setText(f"Опорная точка A: [{p1[0]:6.2f}, {p1[1]:.2f}, 1]")
        self.coord_label2.setText(f"Опорная точка B: [{p2[0]:6.2f}, {p2[1]:.2f}, 1]")
        self.coord_label3.setText(f"Опорная точка C: [{p3[0]:6.2f}, {p3[1]:.2f}, 1]")
        self.coord_label4.setText(f"Опорная точка D: [{p4[0][0]:6.2f}, {p4[0][1]:.2f}, 1]")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())