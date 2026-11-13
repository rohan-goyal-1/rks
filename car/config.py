# ===== SWITCHES =====

# 'sim' or 'hardware'
env = 'sim'
use_pid = True
use_gyro = True
live_plot = True

# ===== CAR =====

# meters
wheel_radius = 0.041021
wheelbase = 0.0889
track_width = 0.2286

# fl, fr, rl, rr
counts_per_rev = (135234 / 112.3, 134542 / 111.8,
                  138728 / 116.0, 135162 / 111.5)

# -1 flips a backwards encoder
sides = (-1, 1, -1, 1)
gyro_sign = 1

# ===== CALIBRATION =====

# paste from calibrate_speed.py, m/s per wheel at each power %
powers = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
speeds = [
    [0, 0.0, 0.0, 0.0, 0.188, 0.266, 0.32, 0.362, 0.394, 0.41, 0.483],
    [0, 0.0, 0.0, 0.0, 0.17, 0.246, 0.304, 0.343, 0.378, 0.399, 0.477],
    [0, 0.0, 0.0, 0.0, 0.197, 0.269, 0.323, 0.363, 0.4, 0.42, 0.5],
    [0, 0.0, 0.0, 0.0, 0.187, 0.258, 0.309, 0.349, 0.381, 0.399, 0.473],
]

# m/s at speed 100
max_speed = 0.38

# ===== CONTROL =====

# trim = max power % the wheel pid can add or remove
wheel_pid = (50, 100, 0)
trim = 20

# 1 = no smoothing
smoothing = 0.5

# seconds of no wheel pid at the start of a move
settle_time = 0.3

# heading_trim = max rad/s the heading pid can add
heading_pid = (3, 1, 0)
heading_trim = 1.5

dt = 0.02
stop_time = 0.5
