import time
import busio
import numpy as np
import RPi.GPIO as GPIO
from adafruit_pca9685 import PCA9685
from simple_pid import PID
import config

# ===== BOARD SETUP =====

GPIO.setmode(GPIO.BCM)

i2c = busio.I2C(3, 2)
pca = PCA9685(i2c)
pca.frequency = 1000

# output enable is active low
PWMOEN = 4
GPIO.setup(PWMOEN, GPIO.OUT)
GPIO.output(PWMOEN, 0)


# ===== WHEELS =====

class Wheel:
    def __init__(self, number, en, in1, in2, a, b):
        self.number = number

        # en = power, in1/in2 = direction
        self.en = pca.channels[en]
        self.in1 = pca.channels[in1]
        self.in2 = pca.channels[in2]

        # encoder a/b
        self.a = a
        self.b = b

        self.count = 0
        self.last_count = 0
        self.speed = 0
        self.target = 0

        # trims around the table power
        self.pid = PID(*config.wheel_pid, setpoint=0)
        self.pid.output_limits = (-config.trim, config.trim)

        GPIO.setup(a, GPIO.IN)
        GPIO.setup(b, GPIO.IN)
        GPIO.add_event_detect(a, GPIO.BOTH, callback=self.pulse)

    def pulse(self, channel):
        if GPIO.input(self.a) != GPIO.input(self.b):
            self.count += 1
        else:
            self.count -= 1

    # en first so there's no full power kick after a brake
    def move(self, power):
        power = max(-100, min(100, power))
        self.en.duty_cycle = int(abs(power) * 0xFFFF / 100)
        if power > 0:
            self.in1.duty_cycle = 0xFFFF
            self.in2.duty_cycle = 0
        else:
            self.in1.duty_cycle = 0
            self.in2.duty_cycle = 0xFFFF

    # both high + en full = short brake on l298n and tb6612
    def brake(self):
        self.in1.duty_cycle = 0xFFFF
        self.in2.duty_cycle = 0xFFFF
        self.en.duty_cycle = 0xFFFF

    def read(self, dt):
        count = self.count
        ticks = config.sides[self.number] * (count - self.last_count)
        self.last_count = count
        revs = ticks / config.counts_per_rev[self.number]
        new = revs / dt * 2 * np.pi * config.wheel_radius

        # ema smoothing
        self.speed = self.speed + config.smoothing * (new - self.speed)
        return self.speed

    def control(self, target, dt, settling):
        speed = self.read(dt)

        if target == 0:
            self.brake()
            self.pid.reset()
            self.target = 0
            return speed

        # feedforward from the calibration table
        table = config.speeds[self.number]
        power = np.interp(abs(target), table, config.powers)
        if target < 0:
            power = -power

        # no pid while settling or right after flipping direction
        if settling or target * self.target < 0:
            self.pid.reset()
        elif config.use_pid:
            self.pid.setpoint = target
            power = power + self.pid(speed)

        # pid can't push against the target direction
        if target > 0:
            power = max(0, power)
        else:
            power = min(0, power)

        self.target = target
        self.move(power)
        return speed


# fl, fr, rl, rr
wheels = [Wheel(0, 4, 5, 6, 22, 10), Wheel(1, 0, 1, 2, 17, 27),
          Wheel(2, 12, 13, 14, 5, 6), Wheel(3, 8, 9, 10, 9, 11)]

# ===== GYRO =====

# bias = average of 100 readings at rest, rad/s
mpu = None
bias = 0
if config.use_gyro:
    import adafruit_mpu6050
    mpu = adafruit_mpu6050.MPU6050(i2c)
    print('zeroing gyro dont touch the car')
    total = 0
    for i in range(100):
        total += mpu.gyro[2]
        time.sleep(0.01)
    bias = total / 100

# ===== DRIVER =====

# start of the current move, 0 = stopped
started = 0


def step(targets, dt):
    global started
    if started == 0:
        started = time.time()
    settling = time.time() - started < config.settle_time

    speeds = []
    for i in range(4):
        speeds.append(wheels[i].control(targets[i], dt, settling))

    rate = None
    if config.use_gyro:
        rate = config.gyro_sign * (mpu.gyro[2] - bias)
    return speeds, rate


def stop():
    global started
    started = 0
    for wheel in wheels:
        wheel.brake()
        wheel.target = 0
        wheel.pid.reset()


# outputs off after braking = wheels spin free
def destroy():
    for wheel in wheels:
        wheel.brake()
    GPIO.output(PWMOEN, 1)
    GPIO.cleanup()
