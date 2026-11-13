import time
import matplotlib.pyplot as plt
import numpy as np
import config

# ===== RECORDED DATA =====

xs = []
ys = []

pxs = []
pys = []
wall_x = []
wall_y = []

# one per step, replay reads these
frames = []
last_draw = 0
names = ['fl', 'fr', 'rl', 'rr']

# ===== FIGURE =====

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

# black needles are wider so they show behind the red ones
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


# ===== RECORDING =====

def update(x, y, heading, speeds, px, py, planned, targets):
    global last_draw
    xs.append(x)
    ys.append(y)
    pxs.append(px)
    pys.append(py)
    frames.append([x, y, heading, speeds, px, py, planned, targets])

    # redraw at most every 0.1 s, drawing is slow
    if config.live_plot and time.time() - last_draw > 0.1:
        draw(len(frames) - 1)
        plt.pause(0.001)
        last_draw = time.time()


def dots(x, y):
    path_ax.plot(x, y, 'ko', markersize=4)


def wall(points):
    wx = [p[0] for p in points]
    wy = [p[1] for p in points]
    path_ax.plot(wx, wy, color='tab:blue', lw=3)

    # fit the path panel to every wall so far
    wall_x.extend(wx)
    wall_y.extend(wy)
    path_ax.set(xlim=(min(wall_x) - 0.2, max(wall_x) + 0.2),
                ylim=(min(wall_y) - 0.2, max(wall_y) + 0.2))


# ===== DRAWING =====

# mecanum forward kinematics
def body(w):
    fwd = (w[0] + w[1] + w[2] + w[3]) / 4
    lft = (-w[0] + w[1] + w[2] - w[3]) / 4
    return fwd, lft


# up = 0, right = +max_speed, left = -max_speed
def needle(speed):
    angle = max(-1, min(1, speed / config.max_speed)) * np.pi / 2
    return np.sin(angle), np.cos(angle)


def draw(i):
    x, y, heading, speeds, px, py, planned, targets = frames[i]

    path.set_data(xs[:i + 1], ys[:i + 1])
    plan_path.set_data(pxs[:i + 1], pys[:i + 1])
    arrow.set_offsets([x, y])
    arrow.set_UVC(np.cos(heading), np.sin(heading))
    plan_arrow.set_offsets([px, py])
    plan_arrow.set_UVC(np.cos(planned), np.sin(planned))

    # car panel: up = forward, left = left
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

    # every 5th frame = 0.1 s of car time per draw
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
