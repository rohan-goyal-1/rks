import numpy as np

drawer = None


def start():
    global drawer
    from drawer import drawer as draw_window
    drawer = draw_window((-10, 10), (-10, 10))


def line(start, end, speed, heading_offset):
    drawer.start_at(start)
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    length = np.sqrt(dx**2 + dy**2)
    if length == 0:
        return
    ux = dx / length
    uy = dy / length
    heading = np.degrees(np.arctan2(uy, ux)) + heading_offset
    drawer.turn_to(heading)
    distance = 0
    while distance < length:
        step = min(1, length - distance)
        distance += step
        x = start[0] + ux * distance
        y = start[1] + uy * distance
        drawer.add_point(x, y, heading, step / speed)


def go_ahead(start, end, speed):
    line(start, end, speed, 0)


def go_back(start, end, speed):
    line(start, end, speed, 180)


def shift_left(start, end, speed):
    line(start, end, speed, -90)


def shift_right(start, end, speed):
    line(start, end, speed, 90)


def upper_right(start, end, speed):
    line(start, end, speed, 45)


def upper_left(start, end, speed):
    line(start, end, speed, -45)


def lower_right(start, end, speed):
    line(start, end, speed, 135)


def lower_left(start, end, speed):
    line(start, end, speed, -135)


def turn_left(angle, speed):
    drawer.start_at((0, 0))
    drawer.turn_by(angle, speed)


def turn_right(angle, speed):
    drawer.start_at((0, 0))
    drawer.turn_by(-angle, speed)


def semi_circle(start, end, speed, clockwise):
    center = ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2)
    radius = np.sqrt((start[0] - center[0])**2 + (start[1] - center[1])**2)
    angle = np.degrees(np.arctan2(start[1] - center[1], start[0] - center[0]))
    direction = -1 if clockwise else 1
    drawer.start_at(start)
    drawer.turn_to(angle + direction * 90)
    remaining = 180
    while remaining > 0:
        step = min(10, remaining)
        angle += direction * step
        remaining -= step
        theta = np.radians(angle)
        x = center[0] + radius * np.cos(theta)
        y = center[1] + radius * np.sin(theta)
        drawer.add_point(x, y, angle + direction * 90, step / speed)


def stop_car():
    pass


def finish():
    drawer.finish()


def destroy():
    drawer.close()
