import time
import numpy as np
import config
import hardware

names = ['fl', 'fr', 'rl', 'rr']


def main():
    print('put the car up on something so the wheels spin free')
    time.sleep(3)
    powers = [0]
    table = [[0], [0], [0], [0]]
    row = []
    for power in range(10, 101, 10):
        for wheel in hardware.wheels:
            wheel.move(power)
        time.sleep(1)
        before = []
        for wheel in hardware.wheels:
            before.append(wheel.count)
        time.sleep(2)
        powers.append(power)
        row = []
        for i in range(4):
            ticks = config.sides[i] * (hardware.wheels[i].count - before[i])
            revs = ticks / config.counts_per_rev[i]
            speed = round(revs / 2 * 2 * np.pi * config.wheel_radius, 3)
            row.append(speed)
            table[i].append(max(speed, table[i][-1]))
        print(power, row)
    hardware.stop()
    print()
    print('powers =', powers)
    print('speeds = [')
    for i in range(4):
        print('    ' + str(table[i]) + ',')
    print(']')
    print('max_speed =', round(0.8 * min(row), 2))
    for i in range(4):
        if row[i] < 0:
            print(names[i], 'is backwards, flip it in sides')
    hardware.destroy()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        hardware.destroy()
        print('stopped')
