import math

from PyQt6.QtCore import QTimer, Qt, QRect
from PyQt6.QtGui import QPixmap, QPainter, QPen, QColor
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout

from .fluid import Fluid


CANVAS_WIDTH = 1000
CANVAS_HEIGHT = 700


class Scene(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)

        self.label = QLabel()

        self.frame_num = 0

        layout.addWidget(self.label)
        self.canvas = QPixmap(CANVAS_WIDTH, CANVAS_HEIGHT)
        self.canvas.fill(Qt.GlobalColor.white)
        self.label.setPixmap(self.canvas)

        self.setLayout(layout)

        self.painter = QPainter(self.canvas)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_scene)
        self.timer.start(int(1/30 * 1000))

        self.gravity = -9.81
        self.dt = 1.0 / 20.0
        self.iter_num = 20
        self.frame_num = 0
        self.over_relaxation = 1.9
        self.obstacle_x = 0.1
        self.obstacle_y = 0.9
        self.obstacle_width = 0.09
        self.obstacle_height = 0.21
        self.paused = False
        self.scene_num = 0
        self.show_obstacle = False
        self.show_streamlines = False
        self.show_velocities = False
        self.show_pressure = False
        self.show_smoke = True
        self.fluid = None

        self.sim_height = 1
        self.cScale = CANVAS_HEIGHT / self.sim_height
        self.sim_width = CANVAS_WIDTH / self.cScale

        self.setup_scene()

    def x_coord_change(self, new_x_coord: float):
        """
        Слот для изменения значения слайдера для x координаты
        :param new_x_coord: новое значение x
        :return:
        """
        self.set_obstacle(new_x_coord / 100, self.obstacle_y, False)
        self.simulate()
        self.draw()

    def y_coord_change(self, new_y_coord: float):
        """
        Слот для изменения значения слайдера для y координаты
        :param new_y_coord: новое значение y
        :return:
        """
        self.set_obstacle(self.obstacle_x, new_y_coord / 100, False)
        self.simulate()
        self.draw()

    def width_change(self, new_w):
        """
        Слот для изменения значения слайдера для ширины
        :param new_w: новое значение ширины
        :return:
        """
        self.obstacle_width = new_w / 100
        self.set_obstacle(self.obstacle_x, self.obstacle_y, False)
        self.simulate()
        self.draw()

    def height_change(self, new_h):
        """
        Слот для изменения значения слайдера для высоты
        :param new_h: новое значение высоты
        :return:
        """
        self.obstacle_height = new_h / 100
        self.set_obstacle(self.obstacle_x, self.obstacle_y, False)
        self.simulate()
        self.draw()

    def cX(self, x):  # пересчёт координаты х
        return x * self.cScale

    def cY(self, y):  # пересчёт координаты х
        return CANVAS_HEIGHT - y * self.cScale

    def setup_scene(self):
        """
        Подготовка симуляции
        :return:
        """
        self.iter_num = 5
        self.density = 1000

        res = 100

        dom_height = 1
        dom_width = dom_height / self.sim_height * self.sim_width
        h = dom_height / res

        numx = int(dom_width / h)
        numy = int(dom_height / h)

        self.fluid = Fluid(self.density, numx, numy, h)
        n = self.fluid.num_y

        in_vel = 2.5
        for j in range(self.fluid.num_y):
            for i in range(self.fluid.num_x):
                s = 1  # fluid
                if i == 0 or j == 0 or j == self.fluid.num_y - 1:
                    s = 0.0  # solid
                self.fluid.s[i * n + j] = s

                if i == 1:
                    self.fluid.u[i * n + j] = in_vel
        pipe_h = 0.9 * self.fluid.num_y
        min_j = int(0.5 * self.fluid.num_y - 0.5 * pipe_h)
        max_j = int(0.5 * self.fluid.num_y + 0.5 * pipe_h)

        for j in range(min_j, max_j):
            self.fluid.m[j] = 0

        self.set_obstacle(self.obstacle_x, self.obstacle_y, True)

        self.gravity = 0

        self.show_pressure = False
        self.show_smoke = True
        self.show_streamlines = False
        self.show_velocities = False

    def draw(self):
        """
        Функция отрисовки
        :return:
        """
        cell_scale = 1
        self.canvas.fill(Qt.GlobalColor.white)
        self.painter.begin(self.canvas)
        pen = QPen()
        pen.setWidth(1)
        n = self.fluid.num_y
        h = self.fluid.h

        color = [255, 255, 255]

        for j in range(self.fluid.num_y):
            for i in range(self.fluid.num_x):
                if self.show_smoke:
                    s = self.fluid.m[i * n + j]
                    color[0] = 255 * s
                    color[1] = 255 * s
                    color[2] = 255 * s

                elif self.fluid.s[i * n + j] == 0:
                    color[0] = 0
                    color[1] = 0
                    color[2] = 0

                x = math.floor(self.cX(i * h))
                y = math.floor(self.cY((j + 1) * h))
                cx = math.floor(self.cScale * cell_scale * h) + 1
                cy = math.floor(self.cScale * cell_scale * h) + 1

                r = int(color[0])
                g = int(color[1])
                b = int(color[2])

                pen.setColor(QColor(r, g, b, 255))
                self.painter.setBrush(QColor(r, g, b, 255))
                self.painter.drawRect(x, y, cx, cy)

        if self.show_obstacle:
            self.painter.setBrush(Qt.GlobalColor.darkCyan)
            rect = QRect(
                int(self.cX(self.obstacle_x)),
                int(self.cY(self.obstacle_y)),
                int(self.cX(self.obstacle_width)),
                int(self.cY(self.obstacle_height))
            )
            self.painter.drawRect(rect)
        self.painter.end()
        self.label.setPixmap(self.canvas)

    def simulate(self):
        """
        Запуск симуляции жидкости
        :return:
        """
        if not self.paused:
            self.fluid.simulate(self.dt, self.gravity, self.iter_num)
            self.frame_num += 1

    def update_scene(self) -> None:
        """
        Функция обновления экрана
        :return:
        """
        self.simulate()
        self.draw()

    def set_obstacle(self, x, y, reset):
        """
        Размещение препятствия
        :param x: х координата
        :param y: у координата
        :param reset: флаг обновления (препятствие только появилось или просто подвинулось)
        :return:
        """
        vx = 0
        vy = 0

        if not reset:
            vx = (x - self.obstacle_x) / self.dt
            vy = (y - self.obstacle_y) / self.dt

        self.obstacle_x = x
        self.obstacle_y = y

        n = self.fluid.num_y

        for j in range(1, self.fluid.num_y - 2):
            for i in range(1, self.fluid.num_x - 2):

                self.fluid.s[i * n + j] = 1

                dx = (i + 0.5) * self.fluid.h - x
                dy = (j + 0.5) * self.fluid.h - y

                cur_x = self.cX((i + 0.5) * self.fluid.h)
                cur_y = self.cY((j + 0.5) * self.fluid.h)


                if (self.cX(self.obstacle_x) <= cur_x <= self.cX(self.obstacle_x) + self.cX(self.obstacle_width)
                        and self.cY(self.obstacle_y) <= cur_y <= self.cY(self.obstacle_y) + self.cY(self.obstacle_height)):
                    self.fluid.s[i * n + j] = 0
                    self.fluid.m[i*n + j] = 1.0

                    self.painter.begin(self.canvas)
                    pen = QPen(Qt.GlobalColor.red)
                    pen.setWidth(int(self.fluid.h) + 10)
                    self.painter.setPen(pen)
                    self.painter.drawPoint(int(self.cX(i * self.fluid.h)), int(self.cY(j * self.fluid.h)))
                    #print(int(self.cX(i * self.fluid.h)), int(self.cY(j * self.fluid.h)))
                    self.painter.end()
                    self.label.setPixmap(self.canvas)

                    self.fluid.u[i * n + j] = vx
                    self.fluid.u[(i + 1) * n + j] = vx
                    self.fluid.v[i * n + j] = vy
                    self.fluid.v[i * n + j + 1] = vy

        self.show_obstacle = True

