import time
import numpy as np
from simple_pid import PID
import config
import display

if config.env == 'hardware':
    import hardware as driver
else:
    import sim as driver

arm = (config.wheelbase + config.track_width) / 2
x = 0
y = 0
heading = 0
planned = 0
px = 0
py = 0
started = False
heading_pid = PID(*config.heading_pid, setpoint=0)
heading_pid.output_limits = (-config.heading_trim, config.heading_trim)


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
    limit = secs
    if angle != 0:
        limit = secs * 2
    begin = time.time()
    last = begin
    while time.time() - begin < limit:
        time.sleep(config.dt)
        now = time.time()
        planned = start + turn * min(now - begin, secs)
        pdt = min(now - begin, secs) - min(last - begin, secs)
        px = px + (forward * np.cos(planned) - left * np.sin(planned)) * pdt
        py = py + (forward * np.sin(planned) + left * np.cos(planned)) * pdt
        spin = turn
        if config.use_gyro:
            heading_pid.setpoint = planned
            spin = spin + heading_pid(heading)
        spin = spin * arm
        fl = forward - left - spin
        fr = forward + left + spin
        rl = forward + left - spin
        rr = forward - left + spin
        step([fl, fr, rl, rr], now - last)
        last = now
        if angle > 0 and heading > start + angle - 0.01:
            break
        if angle < 0 and heading < start + angle + 0.01:
            break
    planned = start + turn * secs


def step(targets, dt):
    global x, y, heading
    s, rate = driver.step(targets, dt)
    fwd = (s[0] + s[1] + s[2] + s[3]) / 4
    lft = (-s[0] + s[1] + s[2] - s[3]) / 4
    if rate is None:
        rate = (-s[0] + s[1] - s[2] + s[3]) / 4 / arm
    heading = heading + rate * dt
    x = x + (fwd * np.cos(heading) - lft * np.sin(heading)) * dt
    y = y + (fwd * np.sin(heading) + lft * np.cos(heading)) * dt
    display.update(x, y, heading, s, px, py, planned, targets)


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
    angle = a2 - a1
    if angle > np.pi:
        angle = angle - 2 * np.pi
    if angle < -np.pi:
        angle = angle + 2 * np.pi
    rate = abs(speed) / 100 * config.max_speed / arm
    secs = abs(angle) / rate
    if angle < 0:
        rate = -rate
    print('turn', round(np.degrees(angle)), 'deg', round(secs, 2), 's')
    drive(0, 0, rate, secs, angle)
    stop_car()


def circle(x1, y1, x2, y2, mode):
    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2
    r = np.hypot(x1 - cx, y1 - cy)
    side = 1
    if mode == 'cw':
        side = -1
    start = np.arctan2(y1 - cy, x1 - cx)
    return r, side, start


def arc(x1, y1, x2, y2, speed, mode='ccw'):
    r, side, start = circle(x1, y1, x2, y2, mode)
    angle = start + side * np.pi / 2
    if speed < 0:
        angle = angle + np.pi
    start_at(x1, y1, angle)
    v = speed / 100 * config.max_speed
    secs = np.pi * r / abs(v)
    print('arc', mode, round(secs, 2), 's')
    drive(v, 0, side * abs(v) / r, secs)
    stop_car()


def mecanum_arc(x1, y1, x2, y2, speed, mode='ccw'):
    r, side, start = circle(x1, y1, x2, y2, mode)
    start_at(x1, y1, start + side * np.pi / 2)
    v = abs(speed) / 100 * config.max_speed
    secs = np.pi * r / v
    print('mecanum arc', mode, round(secs, 2), 's')
    for i in range(20):
        point = start + side * np.pi * (i + 0.5) / 20
        travel = point + side * np.pi / 2 - heading
        drive(v * np.cos(travel), v * np.sin(travel), 0, secs / 20)
    stop_car()


def stop_car():
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
