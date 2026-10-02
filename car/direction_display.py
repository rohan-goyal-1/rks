import matplotlib.pyplot as plt


class direction_display:
    def __init__(self):
        self.fig, self.axes = plt.subplots(1, 2, figsize=(9, 5))
        self.update((0, 0, 0, 0))
        plt.show(block=False)

    def update(self, rpm):
        fl, fr, rl, rr = rpm
        right = (fl - fr - rl + rr) / 4
        forward = (fl + fr + rl + rr) / 4
        turn = (-fl + fr - rl + rr) / 4
        car_ax, wheel_ax = self.axes
        for ax in self.axes:
            ax.clear()
            ax.set_xlim(-1.5, 1.5)
            ax.set_ylim(-1.5, 1.5)
            ax.set_aspect("equal")
            ax.set_xticks([])
            ax.set_yticks([])
        car_ax.set_title("Car (front = up)")
        if right or forward:
            length = (right**2 + forward**2)**0.5
            car_ax.quiver(
                0, 0, right / length, forward / length,
                angles="xy", scale_units="xy", scale=1, color="black",
            )
        else:
            car_ax.plot(0, 0, "ko")
        if turn:
            direction = "left" if turn > 0 else "right"
            state = "Turning " + direction
        elif right or forward:
            state = "Moving"
        else:
            state = "Stopped"
        car_ax.text(0, -1.2, state, ha="center")
        wheel_ax.set_title("Wheels (front = up)")
        positions = [(-0.65, 0.65), (0.65, 0.65),
                     (-0.65, -0.65), (0.65, -0.65)]
        for name, speed, (x, y) in zip(
            ("FL", "FR", "RL", "RR"), rpm, positions,
        ):
            if speed:
                wheel_ax.quiver(
                    x, y, 0, 0.6 if speed > 0 else -0.6,
                    angles="xy", scale_units="xy", scale=1,
                    pivot="mid", color="black",
                )
            else:
                wheel_ax.plot(x, y, "ko")
            wheel_ax.text(x, y - 0.45, f"{name}: {speed:.1f} rpm", ha="center")
        self.fig.canvas.draw_idle()

    def pause(self, seconds):
        plt.pause(seconds)
        if not plt.fignum_exists(self.fig.number):
            raise KeyboardInterrupt

    def close(self):
        plt.close(self.fig)
