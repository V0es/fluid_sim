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
        self.obstacle_width = 0.38
        self.obstacle_height = 0.5
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
        self.set_obstacle(new_x_coord / 100, self.obstacle_y, False)
        self.simulate()
        self.draw()

    def y_coord_change(self, new_y_coord: float):
        self.set_obstacle(self.obstacle_x, new_y_coord / 100, False)
        self.simulate()
        self.draw()

    def width_change(self, new_w):
        self.obstacle_width = new_w / 100
        self.set_obstacle(self.obstacle_x, self.obstacle_y, False)
        self.simulate()
        self.draw()

    def height_change(self, new_h):
        self.obstacle_height = new_h / 100
        self.set_obstacle(self.obstacle_x, self.obstacle_y, False)
        self.simulate()
        self.draw()

    def cX(self, x):
        return x * self.cScale

    def cY(self, y):
        return CANVAS_HEIGHT - y * self.cScale

    def setup_scene(self):
        self.iter_num = 10
        self.density = 1000

        res = 50

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
        cell_scale = 1.1
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
                    #print(self.fluid.m)
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

                #print(color)
                pen.setColor(QColor(r, g, b, 255))
                self.painter.setBrush(QColor(r, g, b, 255))
                self.painter.drawRect(x, y, cx, cy)

        if self.show_obstacle:
            self.painter.setBrush(Qt.GlobalColor.white)
            rect = QRect(
                int(self.cX(self.obstacle_x)),
                int(self.cY(self.obstacle_y)),
                int(self.cX(self.obstacle_width)),
                int(self.cY(1 - self.obstacle_height))
            )
            #print(rect.x(), rect.y(), rect.width(), rect.height())
            self.painter.drawRect(rect)
        self.painter.end()
        self.label.setPixmap(self.canvas)

    def simulate(self):
        if not self.paused:
            self.fluid.simulate(self.dt, self.gravity, self.iter_num)
            self.frame_num += 1

    def update_scene(self) -> None:
        self.simulate()
        self.draw()

    def set_obstacle(self, x, y, reset):
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

                print('curx', cur_x)
                print('cury', cur_y)

                if (self.cX(self.obstacle_x) <= cur_x <= self.cX(self.obstacle_x) + self.cX(self.obstacle_width)
                        and self.cY(self.obstacle_y) <= cur_y <= self.cY(self.obstacle_y) + self.cY(self.obstacle_height)):
                    self.fluid.s[i * n + j] = 0
                    self.fluid.m[i*n + j] = 1.0

                    self.painter.begin(self.canvas)
                    pen = QPen(Qt.GlobalColor.red)
                    pen.setWidth(int(self.fluid.h) + 10)
                    self.painter.setPen(pen)
                    self.painter.drawPoint(int(self.cX(i * self.fluid.h)), int(self.cY(j * self.fluid.h)))
                    print(int(self.cX(i * self.fluid.h)), int(self.cY(j * self.fluid.h)))
                    self.painter.end()
                    self.label.setPixmap(self.canvas)

                    self.fluid.u[i * n + j] = vx
                    self.fluid.u[(i + 1) * n + j] = vx
                    self.fluid.v[i * n + j] = vy
                    self.fluid.v[i * n + j + 1] = vy

        self.show_obstacle = True

