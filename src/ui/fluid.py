import numpy as np

U_FIELD = 0
V_FIELD = 1
S_FIELD = 2


class Fluid:
    def __init__(self, density, num_x, num_y, h):
        self.density = density
        self.num_x = num_x + 2
        self.num_y = num_y + 2
        self.num_cells = self.num_x * self.num_y
        self.p = np.zeros(self.num_cells, dtype=np.float32)
        self.h = h
        self.u = np.zeros(self.num_cells, dtype=np.float32)
        self.v = np.zeros(self.num_cells, dtype=np.float32)
        self.new_u = np.zeros(self.num_cells, dtype=np.float32)
        self.new_v = np.zeros(self.num_cells, dtype=np.float32)
        self.s = np.zeros(self.num_cells, dtype=np.float32)
        self.m = np.ones(self.num_cells, dtype=np.float32)
        self.new_m = np.zeros(self.num_cells, dtype=np.float32)

        self.cnt = 0

    def integrate(self, dt, gravity):
        """
        Суммирование скоростей
        :param dt: шаг времени
        :param gravity: значение ускорения св. падения
        :return:
        """
        n = self.num_y
        for j in range(1, self.num_y):
            for i in range(1, self.num_x - 1):
                if self.s[i * n + j] != 0.0 and self.s[i * n + j - 1] != 0.0:
                    self.v[i * n + j] += gravity * dt

    def solve_incompressibility(self, num_iters, dt, over_relaxation):
        """
        Выполнение условия несжимаемости жидкости
        :param num_iters: число итераций прогонки уравнения
        :param dt: шаг времени
        :param over_relaxation: коэф. успокоения (для устойчивости решения)
        :return:
        """
        n = self.num_y
        cp = self.density * self.h / dt


        for iter_num in range(num_iters):
            for j in range(1, self.num_y - 1):
                for i in range(1, self.num_x - 1):
                    if self.s[i * n + j] == 0.0:
                        continue

                    s = self.s[i * n + j]
                    sx0 = self.s[(i - 1) * n + j]
                    sx1 = self.s[(i + 1) * n + j]
                    sy0 = self.s[i * n + j - 1]
                    sy1 = self.s[i * n + j + 1]
                    s = sx0 + sx1 + sy0 + sy1
                    if s == 0.0:
                        continue

                    div = self.u[(i + 1) * n + j] - self.u[i * n + j] + self.v[i * n + j + 1] - self.v[i * n + j]

                    p = -div / s
                    p *= over_relaxation
                    self.p[i * n + j] += cp * p

                    self.u[i * n + j] -= sx0 * p
                    self.u[(i + 1) * n + j] += sx1 * p
                    self.v[i * n + j] -= sy0 * p
                    self.v[i * n + j + 1] += sy1 * p

    def extrapolate(self):
        """
        Распространиение скоростей на соседние клетки
        :return:
        """
        n = self.num_y
        for i in range(self.num_x):
            self.u[i * n + 0] = self.u[i * n + 1]
            self.u[i * n + self.num_y - 1] = self.u[i * n + self.num_y - 2]
        for j in range(self.num_y):
            self.v[0 * n + j] = self.v[1 * n + j]

    def sample_field(self, x, y, field):
        """
        Расчёт поля скоростей
        :param x: х координата
        :param y: у координата
        :param field: тип поля (U, V, S)
        :return: значение поля в точке
        """
        n = self.num_y
        h = self.h
        h1 = 1.0 / h
        h2 = 0.5 * h

        x = max(min(x, self.num_x * h), h)
        y = max(min(y, self.num_y * h), h)

        dx = 0.0
        dy = 0.0

        if field == U_FIELD:
            f = self.u
            dy = h2
        elif field == V_FIELD:
            f = self.v
            dx = h2
        elif field == S_FIELD:
            f = self.m
            dx = h2
            dy = h2

        x0 = min(int((x - dx) * h1), self.num_x - 1)
        tx = ((x - dx) - x0 * h) * h1
        x1 = min(x0 + 1, self.num_x - 1)

        y0 = min(int((y - dy) * h1), self.num_y - 1)
        ty = ((y - dy) - y0 * h) * h1
        y1 = min(y0 + 1, self.num_y - 1)

        sx = 1.0 - tx
        sy = 1.0 - ty

        val = (sx * sy * f[x0 * n + y0] +
               tx * sy * f[x1 * n + y0] +
               tx * ty * f[x1 * n + y1] +
               sx * ty * f[x0 * n + y1])

        return val

    def avg_u(self, i, j):
        """
        Усреднение U-составляющей скорости
        :param i: номер ячейки по х
        :param j: номер ячейки по y
        :return:
        """
        n = self.num_y
        u = (self.u[i * n + j - 1] + self.u[i * n + j] +
             self.u[(i + 1) * n + j - 1] + self.u[(i + 1) * n + j]) * 0.25
        return u

    def avg_v(self, i, j):
        """
        Усреднение V-составляющей скорости
        :param i: номер ячейки по х
        :param j: номер ячейки по y
        :return:
        """
        n = self.num_y
        v = (self.v[(i - 1) * n + j] + self.v[i * n + j] +
             self.v[(i - 1) * n + j + 1] + self.v[i * n + j + 1]) * 0.25
        return v

    def advect_vel(self, dt):
        """
        Пересчёт предыдущей ячейки жидкости
        :param dt: шаг времени
        :return:
        """
        self.new_u[:] = self.u
        self.new_v[:] = self.v

        n = self.num_y
        h = self.h
        h2 = 0.5 * h

        for j in range(1, self.num_y):
            for i in range(1, self.num_x):
                self.cnt += 1
                # u component
                if self.s[i * n + j] != 0.0 and self.s[(i - 1) * n + j] != 0.0 and j < self.num_y - 1:
                    x = i * h
                    y = j * h + h2
                    u = self.u[i * n + j]
                    v = self.avg_v(i, j)
                    x -= dt * u
                    y -= dt * v
                    u = self.sample_field(x, y, U_FIELD)
                    self.new_u[i * n + j] = u

                # v component
                if self.s[i * n + j] != 0.0 and self.s[i * n + j - 1] != 0.0 and i < self.num_x - 1:
                    x = i * h + h2
                    y = j * h
                    u = self.avg_u(i, j)
                    v = self.v[i * n + j]
                    x -= dt * u
                    y -= dt * v
                    v = self.sample_field(x, y, V_FIELD)
                    self.new_v[i * n + j] = v

        self.u[:] = self.new_u
        self.v[:] = self.new_v

    def advect_smoke(self, dt):
        """
        Расчёт завихрений
        :param dt: шаг времени
        :return:
        """
        self.new_m[:] = self.m

        n = self.num_y
        h = self.h
        h2 = 0.5 * h

        for j in range(1, self.num_y - 1):
            for i in range(1, self.num_x - 1):
                if self.s[i * n + j] != 0.0:
                    u = (self.u[i * n + j] + self.u[(i + 1) * n + j]) * 0.5
                    v = (self.v[i * n + j] + self.v[i * n + j + 1]) * 0.5
                    x = i * h + h2 - dt * u
                    y = j * h + h2 - dt * v

                    self.new_m[i * n + j] = self.sample_field(x, y, S_FIELD)

        self.m[:] = self.new_m

    def simulate(self, dt, gravity, iter_num):
        """
        Вычислить параметры симуляции
        :param dt: шаг времени
        :param gravity: значение гравитации
        :param iter_num: число прогонок решения
        :return:
        """
        self.integrate(dt, gravity)

        self.p.fill(0)

        self.solve_incompressibility(iter_num, dt, 1.9)

        self.extrapolate()
        self.advect_vel(dt)
        self.advect_smoke(dt)
