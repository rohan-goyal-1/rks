import sys

from drawer import Drawer
import shapes


available_functions = ["draw_line", "draw_arc", "draw_semicircle"]
drawer = None


def draw_line(start, end, speed):
    shapes.draw_line(start, end, speed, drawer)


def draw_arc(center, radius, start_angle, end_angle, speed, clockwise):
    shapes.draw_arc(
        center, radius, start_angle, end_angle, speed, clockwise, drawer
    )


def draw_semicircle(start, end, speed, clockwise):
    shapes.draw_semicircle(start, end, speed, clockwise, drawer)


def run_a_func_from_string(command):
    function = command.split("(", 1)
    if function[0] in available_functions:
        exec(command)


def main():
    global drawer

    filename = sys.argv[1]

    print("reading file", filename)

    with open(filename, encoding="utf-8") as command_file:
        commands = command_file.readlines()

    drawer = Drawer((-4, 10), (-2, 6))

    for command in commands:
        command = command.strip()
        if command and not command.startswith("#"):
            print("executing", command)
            run_a_func_from_string(command)

    drawer.finish()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped by user")
