import sys
import car
import config


def main():
    filename = sys.argv[1] if len(sys.argv) > 1 else "moves.txt"

    if "/" not in filename:
        filename = "instructions/" + config.env + "/" + filename

    with open(filename, encoding="utf-8") as myf:
        action_list = myf.readlines()

    try:
        car.start()
        for x in action_list:
            print(x, end="")
            if "#" not in x:
                exec(x, vars(car))
        if config.env == "sim":
            car.finish()
    finally:
        try:
            car.stop_car()
        finally:
            car.destroy()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped and cleanup done")
