import time
import matplotlib.pyplot as plt
import numpy as np
import config

xs = []
ys = []
plan_x = []
plan_y = []
frames = []
last_draw = 0
names = ['fl', 'fr', 'rl', 'rr']

fig, axes = plt.subplots(2, 3, figsize=(11, 6))
fig.suptitle(config.env + '   red = real   black = planned')
path_ax = axes[0, 0]
path_ax.set(xlim=(-1.5, 2), ylim=(-1, 2), aspect='equal', title='path')
plan_path = path_ax.plot([], [], 'k--')[0]
path = path_ax.plot([], [], 'r-')[0]
plan_arrow = path_ax.quiver(0, 0, 1, 0, angles='xy', scale_units='xy',
                            scale=8, color='black')
arrow = path_ax.quiver(0, 0, 1, 0, angles='xy', scale_units='xy', scale=8,
                       color='red')
car_ax = axes[1, 0]
car_ax.set(xlim=(-1.2, 1.2), ylim=(-1.2, 1.2), aspect='equal',
           xticks=[], yticks=[], title='car')
plan_car_arrow = car_ax.quiver(0, 0, 0, 0, angles='xy', scale_units='xy',
                               scale=1, color='black', width=0.012)
car_arrow = car_ax.quiver(0, 0, 0, 0, angles='xy', scale_units='xy',
                          scale=1, color='red')
wheel_axes = [axes[0, 1], axes[0, 2], axes[1, 1], axes[1, 2]]
plan_needles = []
needles = []
for i in range(4):
    ax = wheel_axes[i]
    ax.set(xlim=(-1.2, 1.2), ylim=(-1.2, 1.2), aspect='equal',
           xticks=[], yticks=[], title=names[i])
    plan_needles.append(ax.quiver(0, 0, 0, 1, angles='xy', scale_units='xy',
                                  scale=1, color='black', width=0.012))
    needles.append(ax.quiver(0, 0, 0, 1, angles='xy', scale_units='xy',
                             scale=1, color='red'))
fig.tight_layout()

if config.live_plot:
    plt.ion()
    plt.show()


def update(x, y, heading, speeds, px, py, planned, targets):
    global last_draw
    xs.append(x)
    ys.append(y)
    frames.append([x, y, heading, speeds, px, py, planned, targets])
    if config.live_plot and time.time() - last_draw > 0.1:
        draw(len(frames) - 1)
        plt.pause(0.001)
        last_draw = time.time()


def plan(px, py):
    plan_x.append(px)
    plan_y.append(py)


def show_plan():
    plan_path.set_data(plan_x, plan_y)
    if config.live_plot:
        plt.pause(0.001)


def dots(x, y):
    path_ax.plot(x, y, 'ko', markersize=4)


def body(w):
    fwd = (w[0] + w[1] + w[2] + w[3]) / 4
    lft = (-w[0] + w[1] + w[2] - w[3]) / 4
    return fwd, lft


def needle(speed):
    angle = max(-1, min(1, speed / config.max_speed)) * np.pi / 2
    return np.sin(angle), np.cos(angle)


def draw(i):
    x, y, heading, speeds, px, py, planned, targets = frames[i]
    path.set_data(xs[:i + 1], ys[:i + 1])
    arrow.set_offsets([x, y])
    arrow.set_UVC(np.cos(heading), np.sin(heading))
    plan_arrow.set_offsets([px, py])
    plan_arrow.set_UVC(np.cos(planned), np.sin(planned))
    fwd, lft = body(speeds)
    pfwd, plft = body(targets)
    car_arrow.set_UVC(-lft / config.max_speed, fwd / config.max_speed)
    plan_car_arrow.set_UVC(-plft / config.max_speed, pfwd / config.max_speed)
    car_ax.set_title('car ' + str(round(np.hypot(fwd, lft), 2)) + ' / '
                     + str(round(np.hypot(pfwd, plft), 2)) + ' m/s')
    for w in range(4):
        needles[w].set_UVC(*needle(speeds[w]))
        plan_needles[w].set_UVC(*needle(targets[w]))
        wheel_axes[w].set_title(names[w] + ' ' + str(round(speeds[w], 2))
                                + ' / ' + str(round(targets[w], 2)))


def finish():
    if len(frames) == 0:
        return
    if not config.live_plot:
        print('replaying')
        plt.ion()
        plt.show()
        for i in range(0, len(frames), 5):
            draw(i)
            plt.pause(0.05)
    draw(len(frames) - 1)
    plt.ioff()
    plt.show()
