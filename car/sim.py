# ===== FAKE DRIVER =====

# perfect wheels, no gyro
def step(targets, dt):
    return targets, None


def stop():
    pass


def destroy():
    pass
