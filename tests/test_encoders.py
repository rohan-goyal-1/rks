'''
left: (negative encoder values)
f: 112.3, 135234
r: 116.0, 138728

right:
f: 111.8, 134542
r: 111.5, 135,162
'''


# set up Raspberry Pi GPIO

import test_moves

GPIO = test_moves.GPIO
GPIO.setmode(GPIO.BCM)

# Encoders, GPIO.board pin
# pin 11
S1FR = 17
# pin 13
S2FR = 27

# pin 15
S1FL = 22
# pin 19
S2FL = 10

# pin 21
S1RR = 9
# pin 23
S2RR = 11

# pin 29
S1RL = 5
# pin 31
S2RL = 6

# encoder class


class Encoder:
    def __init__(self, name, S1, S2):
        # for debug
        self.name = name
        # pin
        self.s1 = S1
        # instance
        GPIO.setup(S1, GPIO.IN)
        # pin
        self.s2 = S2
        GPIO.setup(S2, GPIO.IN)
        # value (aState)
        self.aState = 0
        self.bState = 0
        # remember last value (aLastState)
        self.aLastState = 0
        # not needed?
        self.bLastState = 0
        self.counter = 0

    def read(self):
        self.aState = GPIO.input(self.s1)
        self.bState = GPIO.input(self.s2)
        return self.aState, self.bState

    def name(self):
        return self.name

# end of Encoder class


# Set up Encoder instances with connections, GPIO.board (swheel)
# sfl = Encoder("sfl", S1FL, S2FL)
# sfr = Encoder("sfr", S1FR, S2FR)
# srl = Encoder("srl", S1RL, S2RL)
srr = Encoder("srr", S1RR, S2RR)


def readEncoder(swheel):
    # Reads the "current" state of the encoders
    aState, bState = swheel.read()
    # counter = swheel.counter # should not be needed, but += -=?
    # If the previous and the current state are different,  a Pulse has occured
    if aState != swheel.aLastState:
        # If the outputB state is different to the outputA state, rotating
        # clockwise
        if bState != aState:
            swheel.counter += 1
        else:
            swheel.counter -= 1
        print(swheel.name + " position: " + str(swheel.counter))

    swheel.aLastState = aState  # remember last state of a
    # swheel.counter = counter #remember position


def test_Encoders():
    # readEncoder(sfl)
    # readEncoder(sfr)
    # readEncoder(srl)
    readEncoder(srr)


def destroy():
    GPIO.cleanup()


def main():
    print("starting main")
    while True:
        test_Encoders()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        # clean up GPIO
        destroy()
        print("Done")
