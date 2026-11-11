# rks

set `env` in config.py to `'sim'` or `'hardware'`. pid / gyro / live plot switches are in there too

```sh
python3 executor.py instructions/quadrilateral.txt # hw5
python3 executor.py instructions/square.txt # hw8
python3 executor.py instructions/racetrack.txt # hw9
python3 executor.py instructions/racetrack_two_laps.txt # hw10
python3 executor.py instructions/racetrack_fixed_heading.txt # hw11
python3 executor.py instructions/obstacle_course.txt # splines
```

meters. speed is % of max_speed. negative speed = backwards

plot: red = real (encoders + gyro), black = planned. live_plot = False just records and replays it at the end (use that on the hardware if drawing makes it laggy)
