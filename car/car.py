import time
import numpy as np
from simple_pid import PID
from scipy.interpolate import CubicSpline
import config
import display

# ===== DRIVER =====

if config.env == 'hardware':
    import hardware as driver
else:
    import sim as driver

# ===== STATE =====

# mecanum lever arm, lx + ly
arm = (config.wheelbase + config.track_width) / 2

# real pose from odometry
x = 0
y = 0
heading = 0

# planned pose, planned = heading
planned = 0
px = 0
py = 0

started = False

heading_pid = PID(*config.heading_pid, setpoint=0)
heading_pid.output_limits = (-config.heading_trim, config.heading_trim)


# ===== DRIVING =====

# only the first move sets the pose
def start_at(x0, y0, angle):
    global x, y, heading, planned, px, py, started
    if not started:
        x = x0
        y = y0
        px = x0
        py = y0
        heading = angle
        planned = angle
        started = True


def drive(forward, left, turn, secs, angle=0):
    global planned, px, py
    start = planned

    # 2x time so a slow turn can still reach angle
    limit = secs
    if angle != 0:
        limit = secs * 2

    begin = time.time()
    last = begin
    while time.time() - begin < limit:
        time.sleep(config.dt)
        now = time.time()

        # pdt clamps the plan to secs even if the loop runs over
        planned = start + turn * min(now - begin, secs)
        pdt = min(now - begin, secs) - min(last - begin, secs)
        px = px + (forward * np.cos(planned) - left * np.sin(planned)) * pdt
        py = py + (forward * np.sin(planned) + left * np.cos(planned)) * pdt

        go(forward, left, turn, now - last)
        last = now

        if angle > 0 and heading > start + angle - 0.01:
            break
        if angle < 0 and heading < start + angle + 0.01:
            break

    planned = start + turn * secs


def go(forward, left, turn, dt):
    # pid on the error so d doesn't fight planned turns
    spin = turn
    if config.use_gyro:
        spin = spin + heading_pid(heading - planned)
    spin = spin * arm

    # mecanum inverse kinematics
    fl = forward - left - spin
    fr = forward + left + spin
    rl = forward + left - spin
    rr = forward - left + spin
    step([fl, fr, rl, rr], dt)


def step(targets, dt):
    global x, y, heading
    s, rate = driver.step(targets, dt)

    # mecanum forward kinematics
    fwd = (s[0] + s[1] + s[2] + s[3]) / 4
    lft = (-s[0] + s[1] + s[2] - s[3]) / 4

    # no gyro
    if rate is None:
        rate = (-s[0] + s[1] - s[2] + s[3]) / 4 / arm

    heading = heading + rate * dt
    x = x + (fwd * np.cos(heading) - lft * np.sin(heading)) * dt
    y = y + (fwd * np.sin(heading) + lft * np.cos(heading)) * dt

    print('x = ', x, '; y = ', y, '; heading = ', heading)
    display.update(x, y, heading, s, px, py, planned, targets)


# ===== MOVES =====

def line(x1, y1, x2, y2, speed):
    angle = np.arctan2(y2 - y1, x2 - x1)
    if speed < 0:
        angle = angle + np.pi
    start_at(x1, y1, angle)

    dist = np.hypot(x2 - x1, y2 - y1)
    v = speed / 100 * config.max_speed
    secs = dist / abs(v)

    print('line', round(dist, 2), 'm', round(secs, 2), 's')
    drive(v, 0, 0, secs)
    stop_car()


def tank_turn(x1, y1, x2, y2, x3, y3, speed):
    a1 = np.arctan2(y2 - y1, x2 - x1)
    a2 = np.arctan2(y3 - y2, x3 - x2)
    start_at(x2, y2, a1)

    # wrap to -pi..pi
    angle = a2 - a1
    if angle > np.pi:
        angle = angle - 2 * np.pi
    if angle < -np.pi:
        angle = angle + 2 * np.pi

    turn_by(angle, speed)


def turn_by(angle, speed):
    rate = abs(speed) / 100 * config.max_speed / arm
    secs = abs(angle) / rate
    if angle < 0:
        rate = -rate

    print('turn', round(np.degrees(angle)), 'deg', round(secs, 2), 's')
    drive(0, 0, rate, secs, angle)
    stop_car()


# no centre = p1-p2 is the diameter
def circle(x1, y1, x2, y2, mode, center_x, center_y):
    if center_x is None:
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
    r = np.hypot(x1 - center_x, y1 - center_y)

    side = 1
    if mode == 'cw':
        side = -1

    # sweep = 0..2pi going the mode's way
    start = np.arctan2(y1 - center_y, x1 - center_x)
    end = np.arctan2(y2 - center_y, x2 - center_x)
    sweep = (side * (end - start)) % (2 * np.pi)
    return r, side, start, sweep


def arc(x1, y1, x2, y2, speed, mode='ccw', center_x=None, center_y=None):
    r, side, start, sweep = circle(x1, y1, x2, y2, mode, center_x, center_y)
    angle = start + side * np.pi / 2
    if speed < 0:
        angle = angle + np.pi
    start_at(x1, y1, angle)

    v = speed / 100 * config.max_speed
    secs = sweep * r / abs(v)

    print('arc', mode, round(np.degrees(sweep)), 'deg', round(secs, 2), 's')
    drive(v, 0, side * abs(v) / r, secs)
    stop_car()


def mecanum_arc(x1, y1, x2, y2, speed, mode='ccw',
                center_x=None, center_y=None):
    r, side, start, sweep = circle(x1, y1, x2, y2, mode, center_x, center_y)
    start_at(x1, y1, start + side * np.pi / 2)

    v = abs(speed) / 100 * config.max_speed
    secs = sweep * r / v

    # 20 straight pieces, aimed relative to the real heading
    print('mecanum arc', mode, round(np.degrees(sweep)), 'deg',
          round(secs, 2), 's')
    for i in range(20):
        point = start + side * sweep * (i + 0.5) / 20
        travel = point + side * np.pi / 2 - heading
        drive(v * np.cos(travel), v * np.sin(travel), 0, secs / 20)
    stop_car()


# ===== SPLINES =====

def spline(points, speed, fixed=False):
    # d = distance along the waypoints, the spline parameter
    xs = []
    ys = []
    d = [0]
    for i in range(len(points)):
        xs.append(points[i][0])
        ys.append(points[i][1])
        if i > 0:
            d.append(d[-1] + np.hypot(xs[i] - xs[i - 1], ys[i] - ys[i - 1]))

    fx = CubicSpline(d, xs, bc_type='natural')
    fy = CubicSpline(d, ys, bc_type='natural')

    # chop into ~10 cm straight pieces
    n = int(d[-1] / 0.1) + 1
    t = np.linspace(0, d[-1], n + 1)
    sx = fx(t)
    sy = fy(t)
    lengths = np.hypot(np.diff(sx), np.diff(sy))
    angles = np.unwrap(np.arctan2(np.diff(sy), np.diff(sx)))

    # shift by 2pi so it lines up with planned after earlier turns
    start_at(sx[0], sy[0], angles[0])
    angles = angles + 2 * np.pi * round((planned - angles[0]) / (2 * np.pi))

    display.dots(xs, ys)
    v = abs(speed) / 100 * config.max_speed
    print('spline', round(lengths.sum(), 2), 'm', n, 'pieces')

    for i in range(n):
        secs = lengths[i] / v

        # fixed: slide relative to real heading
        if fixed:
            travel = angles[i] - heading
            drive(v * np.cos(travel), v * np.sin(travel), 0, secs)

        # else: end the piece facing between it and the next one
        else:
            end = (angles[i] + angles[min(i + 1, n - 1)]) / 2
            drive(v, 0, (end - planned) / secs, secs)

    stop_car()


def mecanum_spline(points, speed):
    spline(points, speed, True)


# ===== COURSE =====

def wall(points):
    display.wall(points)


# ===== STOPPING =====

def stop_car():
    # keep stepping so odometry catches the car slowing down
    begin = time.time()
    last = begin
    while time.time() - begin < config.stop_time:
        time.sleep(config.dt)
        now = time.time()
        step([0, 0, 0, 0], now - last)
        last = now

    driver.stop()
    heading_pid.reset()


def simulate():
    stop_car()
    print('done')
    display.finish()


def destroy():
    driver.destroy()
