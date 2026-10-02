# Car

From this folder:

```bash
python3 executor.py [PATH/TO/INSTRUCTION/SET]
```

Set `env` in `config.py` to `sim` or `hardware`. The runner uses `instructions/sim/` locally and
`instructions/hardware/` on the car.

Simulation:
```
go_ahead((2, 2), (8, 2), 1)
semi_circle((8, 2), (8, 8), 10, False)
turn_left(90, 20)
```
Straight moves take start, end, speed in units/second. Semicircles take start, end, speed in degrees/second, clockwise. Turns take degrees, degrees/second.

Hardware:
```
go_ahead(65, 3.15)
stop_car()
semi_circle(65, 6.8)
stop_car()
```
Hardware uses power percent and seconds. Encoder diagnostics print RPM using each wheel’s `counts_per_rev` ratio.
