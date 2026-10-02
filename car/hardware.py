import time

import busio

from adafruit_pca9685 import PCA9685 as pca9685

import RPi.GPIO as gpio

scl = 3
sda = 2

gpio.setmode(gpio.BCM)

i2c = busio.I2C(scl, sda)
pca = pca9685(i2c)
pca.frequency = 1000

ena_fr = 0
in1_fr = 1
in2_fr = 2

in3_fl = 5
in4_fl = 6
enb_fl = 4

ena_rr = 8
in1_rr = 9
in2_rr = 10

in3_rl = 13
in4_rl = 14
enb_rl = 12

s1_fr = 17
s2_fr = 27

s1_fl = 22
s2_fl = 10

s1_rr = 9
s2_rr = 11

s1_rl = 5
s2_rl = 6

pwmoen = 4
pwm_o_en = gpio.setup(pwmoen, gpio.OUT)

push_button = 26
gpio.setup(push_button, gpio.IN)
old_pushb = 0


def read_push():
    global old_pushb
    pushb = gpio.input(push_button)
    if pushb != old_pushb:
        old_pushb = pushb
        return True, pushb
    else:
        return False, pushb


def valmap(value, istart, istop, ostart, ostop):
    return ostart + (ostop - ostart) * ((value - istart) / (istop - istart))


def get_pwm_per(value):
    return int(valmap(value, 0, 100, 0, 0xFFFF))


high = 0xFFFF
low = 0
display = None
display_counts = (0, 0, 0, 0)
display_time = None

encoder_calibration = {
    "fl": {"rpm": 112.3, "counts_per_minute": -135234},
    "rl": {"rpm": 116.0, "counts_per_minute": -138728},
    "fr": {"rpm": 111.8, "counts_per_minute": 134542},
    "rr": {"rpm": 111.5, "counts_per_minute": 135162},
}

counts_per_rev = {
    name: abs(data["counts_per_minute"]) / data["rpm"]
    for name, data in encoder_calibration.items()
}


class wheel:
    def __init__(self, name, en_ch, in1_ch, in2_ch):
        self.name = name
        self.en = pca.channels[en_ch]
        self.in1 = pca.channels[in1_ch]
        self.in2 = pca.channels[in2_ch]

    def move(self, power):
        self.in1.duty_cycle = high if power > 0 else low
        self.in2.duty_cycle = low if power > 0 else high
        self.en.duty_cycle = get_pwm_per(
            power) if power > 0 else get_pwm_per(-power)

    def brake(self):
        self.in1.duty_cycle = low
        self.in2.duty_cycle = low


rl = wheel("rl", enb_rl, in3_rl, in4_rl)
rr = wheel("rr", ena_rr, in1_rr, in2_rr)
fl = wheel("fl", enb_fl, in3_fl, in4_fl)
fr = wheel("fr", ena_fr, in1_fr, in2_fr)


class encoder:
    def __init__(self, name, s1, s2, side):
        self.name = name
        self.s1 = s1
        gpio.setup(s1, gpio.IN)
        self.s2 = s2
        gpio.setup(s2, gpio.IN)
        self.a_state = 0
        self.b_state = 0
        self.a_last_state = 0
        self.b_last_state = 0
        self.counter = 0
        self.total_count = 0
        self.last_counter = 0
        self.aturn = 0
        self.bturn = 0
        self.speed = 0
        self.time = time.perf_counter_ns()
        self.last_time = self.time
        self.side = side

    def read(self):
        self.a_state = gpio.input(self.s1)
        self.b_state = gpio.input(self.s2)
        self.time = time.perf_counter_ns()
        return self.a_state, self.b_state

    def read_turn(self):
        return self.aturn, self.bturn

    def read_name(self):
        return self.name

    def read_encoder(self):
        a_state, b_state = self.read()

        if a_state != self.a_last_state:
            if b_state != a_state:
                self.counter += 1
                self.total_count += 1
            else:
                self.counter -= 1
                self.total_count -= 1

        if b_state != self.b_last_state:
            self.bturn += 1

        self.a_last_state = a_state
        self.b_last_state = b_state

    def read_encoder_test(self):
        self.read_encoder()

    def callback_encoder(self, channel):
        self.read_encoder()
        print(self.counter)

    def read_speed(self):
        if self.time != self.last_time:
            self.speed = self.side * \
                (self.counter - self.last_counter)/(self.time - self.last_time)
        else:
            self.speed = 0

        self.last_time = self.time
        self.last_counter = self.counter

        return self.speed

    def reset_speed(self):
        self.speed = 0
        self.counter = 0
        self.last_counter = 0

        self.time = time.perf_counter_ns()
        self.last_time = time.perf_counter_ns()


sfl = encoder("sfl", s1_fl, s2_fl, -1)
sfr = encoder("sfr", s1_fr, s2_fr, 1)
srl = encoder("srl", s1_rl, s2_rl, -1)
srr = encoder("srr", s1_rr, s2_rr, 1)


def test_encoders():
    sfl.read_encoder_test()
    sfr.read_encoder_test()
    srl.read_encoder_test()
    srr.read_encoder_test()


gpio.add_event_detect(sfl.s1, gpio.BOTH, callback=sfl.callback_encoder)
gpio.add_event_detect(sfr.s1, gpio.BOTH, callback=sfr.callback_encoder)
gpio.add_event_detect(srl.s1, gpio.BOTH, callback=srl.callback_encoder)
gpio.add_event_detect(srr.s1, gpio.BOTH, callback=srr.callback_encoder)


def start():
    global display, display_counts, display_time
    gpio.output(pwmoen, 1)
    from direction_display import direction_display
    display = direction_display()
    display_counts = tuple(
        sensor.total_count for sensor in (sfl, sfr, srl, srr)
    )
    display_time = time.perf_counter_ns()
    stop_car()
    gpio.output(pwmoen, 0)


def destroy():
    gpio.output(pwmoen, 1)
    gpio.cleanup()
    if display is not None:
        display.close()


def test_speed():
    print('fl rpm: ', sfl.read_speed() * 60e9 / counts_per_rev['fl'])
    print('fr rpm: ', sfr.read_speed() * 60e9 / counts_per_rev['fr'])
    print('rl rpm: ', srl.read_speed() * 60e9 / counts_per_rev['rl'])
    print('rr rpm: ', srr.read_speed() * 60e9 / counts_per_rev['rr'])


def stop_car():
    rl.brake()
    rr.brake()
    fl.brake()
    fr.brake()

    wait(1)
    sfl.reset_speed()
    srr.reset_speed()
    srl.reset_speed()
    sfr.reset_speed()


def update_display():
    global display_counts, display_time
    encoders = (sfl, sfr, srl, srr)
    counts = tuple(sensor.total_count for sensor in encoders)
    now = time.perf_counter_ns()
    elapsed = now - display_time
    rpm = tuple(
        sensor.side * (count - previous) * 60e9
        / elapsed / counts_per_rev[name]
        for sensor, count, previous, name in zip(
            encoders, counts, display_counts, ('fl', 'fr', 'rl', 'rr'),
        )
    )
    display_counts = counts
    display_time = now
    display.update(rpm)


def wait(for_secs):
    if display is None:
        time.sleep(for_secs)
        return
    end = time.monotonic() + for_secs
    remaining = end - time.monotonic()
    while remaining > 0:
        display.pause(min(0.05, remaining))
        update_display()
        remaining = end - time.monotonic()


def go_ahead(power, for_secs):
    rl.move(power)
    rr.move(power)
    fl.move(power)
    fr.move(power)
    wait(for_secs)


def go_back(power, for_secs):
    rr.move(-power)
    rl.move(-power)
    fr.move(-power)
    fl.move(-power)
    wait(for_secs)


def turn_right(power, for_secs):
    rl.move(power)
    rr.move(-power)
    fl.move(power)
    fr.move(-power)
    wait(for_secs)


def turn_left(power, for_secs):
    rr.move(power)
    rl.move(-power)
    fr.move(power)
    fl.move(-power)
    wait(for_secs)


def shift_left(power, for_secs):
    fr.move(power)
    rr.move(-power)
    rl.move(power)
    fl.move(-power)
    wait(for_secs)


def shift_right(power, for_secs):
    fr.move(-power)
    rr.move(power)
    rl.move(-power)
    fl.move(power)
    wait(for_secs)


def upper_right(power, for_secs):
    rr.move(power)
    fl.move(power)
    wait(for_secs)


def lower_left(power, for_secs):
    rr.move(-power)
    fl.move(-power)
    wait(for_secs)


def upper_left(power, for_secs):
    fr.move(power)
    rl.move(power)
    wait(for_secs)


def lower_right(power, for_secs):
    fr.move(-power)
    rl.move(-power)
    wait(for_secs)


def front_left(power, for_secs):
    print("Front left ahead @ " + str(power) +
          "% for " + str(for_secs) + " secs.")
    fl.move(power)
    wait(for_secs)
    test_speed()
    stop_car()


def front_right(power, for_secs):
    print("Front right ahead @ " + str(power) +
          "% for " + str(for_secs) + " secs.")
    fr.move(power)
    wait(for_secs)
    test_speed()
    stop_car()


def rear_left(power, for_secs):
    print("Rear left ahead @ " + str(power) +
          "% for " + str(for_secs) + " secs.")
    rl.move(power)
    wait(for_secs)
    test_speed()
    stop_car()


def rear_right(power, for_secs):
    print("Rear right ahead @ " + str(power) +
          "% for " + str(for_secs) + " secs.")
    rr.move(power)
    wait(for_secs)
    test_speed()
    stop_car()


def coast_all(for_secs):
    print("Coast forSecs " + str(for_secs) + " secs.")
    rl.move(0)
    rr.move(0)
    fr.move(0)
    rr.move(0)
    wait(for_secs)
    stop_car()


def semi_circle(power, for_secs):
    rl.move(power * 0.55)
    rr.move(power)
    fl.move(power * 0.55)
    fr.move(power)
    wait(for_secs)
