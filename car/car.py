import config

if config.env == "hardware":
    import hardware as backend

    front_left = backend.front_left
    front_right = backend.front_right
    rear_left = backend.rear_left
    rear_right = backend.rear_right
    coast_all = backend.coast_all
    test_speed = backend.test_speed
    test_encoders = backend.test_encoders
    read_push = backend.read_push
else:
    import sim as backend

    finish = backend.finish

start = backend.start
destroy = backend.destroy
stop_car = backend.stop_car
go_ahead = backend.go_ahead
go_back = backend.go_back
turn_right = backend.turn_right
turn_left = backend.turn_left
shift_left = backend.shift_left
shift_right = backend.shift_right
upper_right = backend.upper_right
lower_left = backend.lower_left
upper_left = backend.upper_left
lower_right = backend.lower_right
semi_circle = backend.semi_circle
