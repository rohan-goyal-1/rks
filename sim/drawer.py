import matplotlib.pyplot as plt


class Drawer:
    def __init__(self, xlim, ylim):
        self.plot_x = []
        self.plot_y = []

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
        input("Press enter to exit: ")
        plt.close(self.fig)
