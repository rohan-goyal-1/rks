from simple_pid import PID
pid = PID(1, 0.1, 0.05, setpoint = 1)
v =controlled_system.update(0)

while True:
    control = pid(v)
    v = controlled_system.update(control)
