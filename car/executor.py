import sys
import car


def main():
    filename = 'instructions/square.txt'
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    print('running', filename)
    with open(filename) as file:
        commands = file.readlines()

    for command in commands:
        if '#' not in command:
            print(command, end='')
            exec(command, vars(car))
    car.destroy()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        car.destroy()
        print('stopped')
