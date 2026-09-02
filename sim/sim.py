import matplotlib.pyplot as plt
import numpy as np


class Drawer:
    def __init__(self, xlim, ylim):
        self.plot_x = []
        self.plot_y = []

        plt.ion()
        self.fig, self.ax = plt.subplots()

        self.xlim = xlim
        self.ylim = ylim

    def start_at(self, point):
        if not self.plot_x:
            self.plot_x.append(point[0])
            self.plot_y.append(point[1])

    def add_point(self, x, y, pause):
        self.plot_x.append(x)
        self.plot_y.append(y)

        self.ax.clear()
        self.ax.set_xlim(self.xlim)
        self.ax.set_ylim(self.ylim)
        self.ax.set_aspect("equal")

        self.ax.plot(self.plot_x, self.plot_y, "b-")
        self.ax.plot(x, y, "ro")

        plt.pause(pause)

    def finish(self):
        input("Press enter to exit:")
        plt.close(self.fig)
        plt.ioff()


def draw_line(start, end, speed, drawer):
    drawer.start_at(start)

    dx = end[0] - start[0]
    dy = end[1] - start[1]

    length = np.sqrt(dx**2 + dy**2)

    ux = dx / length
    uy = dy / length

    distance = 0

    while distance < length:
        step = min(1, length - distance)
        distance += step

        x = start[0] + ux * distance
        y = start[1] + uy * distance

        drawer.add_point(x, y, step / speed)


def draw_arc(center, radius, start_angle, end_angle, speed, clockwise, drawer):
    if clockwise:
        if end_angle > start_angle:
            end_angle -= 360
        angle_step = -1
    else:
        if end_angle < start_angle:
            end_angle += 360
        angle_step = 1

    angle = start_angle

    while angle != end_angle:
        remaining = abs(end_angle - angle)
        step = min(10, remaining)

        angle += angle_step * step

        theta = np.radians(angle)

        x = center[0] + radius * np.cos(theta)
        y = center[1] + radius * np.sin(theta)

        drawer.add_point(x, y, step / speed)


def draw_semicircle(start, end, speed, clockwise, drawer):
    drawer.start_at(start)

    center = ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2)

    radius = np.sqrt((start[0] - center[0])**2 + (start[1] - center[1])**2)

    start_angle = np.degrees(
        np.arctan2(start[1] - center[1], start[0] - center[0])
    )

    if clockwise:
        end_angle = start_angle - 180
    else:
        end_angle = start_angle + 180

    draw_arc(center, radius, start_angle, end_angle, speed, clockwise, drawer)


def draw_quad(points, speed, drawer):
    for i in range(4):
        draw_line(points[i], points[(i + 1) % 4], speed, drawer)


def main():
    drawer = Drawer((-4, 10), (-2, 6))

    top_left = (0, 4)
    top_right = (6, 4)
    bottom_right = (6, 0)
    bottom_left = (0, 0)

    draw_line(top_left, top_right, 1, drawer)
    draw_semicircle(top_right, bottom_right, 10, True, drawer)
    draw_line(bottom_right, bottom_left, 1, drawer)
    draw_semicircle(bottom_left, top_left, 10, True, drawer)

    drawer.finish()


if __name__ == "__main__":
    main()
