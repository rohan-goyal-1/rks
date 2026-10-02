import matplotlib.pyplot as plt
import numpy as np


class drawer:
    def __init__(self, xlim, ylim):
        self.plot_x = []
        self.plot_y = []
        self.arrow_x = []
        self.arrow_y = []
        self.arrow_heading = []
        self.heading = 0

        self.fig, self.ax = plt.subplots()

        self.xlim = xlim
        self.ylim = ylim

        self.tank_turn_speed = 10

    def start_at(self, point):
        if not self.plot_x:
            self.plot_x.append(point[0])
            self.plot_y.append(point[1])

    def add_point(self, x, y, heading, pause):
        self.plot_x.append(x)
        self.plot_y.append(y)
        self.heading = heading

        self.draw(x, y, pause)

    def turn_to(self, heading):
        turn = (heading - self.heading + 180) % 360 - 180

        self.turn_by(turn, self.tank_turn_speed)

    def turn_by(self, turn, speed):
        while turn != 0:
            step = min(10, abs(turn))
            step = step if turn > 0 else -step
            self.heading += step
            turn -= step
            self.draw(self.plot_x[-1], self.plot_y[-1],
                      abs(step) / speed)

    def draw(self, x, y, pause):
        self.arrow_x.append(x)
        self.arrow_y.append(y)
        self.arrow_heading.append(self.heading)

        self.ax.clear()
        self.ax.set_xlim(self.xlim)
        self.ax.set_ylim(self.ylim)
        self.ax.set_aspect("equal")

        self.ax.plot(self.plot_x, self.plot_y, "b-")
        angles = np.radians(self.arrow_heading)
        self.ax.quiver(
            self.arrow_x,
            self.arrow_y,
            np.cos(angles),
            np.sin(angles),
            color="b",
            pivot="mid",
            angles="xy",
        )
        angle = angles[-1]
        self.ax.quiver(
            x,
            y,
            np.cos(angle),
            np.sin(angle),
            color="r",
            pivot="mid",
            angles="xy",
        )

        plt.pause(pause)

    def finish(self):
        input("Press enter to exit: ")
        self.close()

    def close(self):
        plt.close(self.fig)
