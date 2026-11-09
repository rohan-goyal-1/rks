from simple_pid import PID


def run(controlled_system):
    pid = PID(1, 0.1, 0.05, setpoint=1)
    value = controlled_system.update(0)
    while True:
        value = controlled_system.update(pid(value))
