import numpy as np


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


def draw_arc(center, radius, start_angle, end_angle,
             speed, clockwise, drawer):
    if clockwise:
        if end_angle > start_angle:
            end_angle -= 360
        angle_step = -1
    else:
        if end_angle < start_angle:
            end_angle += 360
        angle_step = 1

    start_radians = np.radians(start_angle)
    drawer.start_at(
        (
            center[0] + radius * np.cos(start_radians),
            center[1] + radius * np.sin(start_radians),
        )
    )

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

    draw_arc(center, radius, start_angle, end_angle,
             speed, clockwise, drawer)
