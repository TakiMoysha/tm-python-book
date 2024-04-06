import multiprocessing

from time import sleep
from random import random
from multiprocessing import Process

class TakiProcess(Process):
    def __init__(self, stop_event, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stop_event = stop_event
        self.sleep_time = 0

    def run(self):
        self.sleep_time = random()
        while True:
            print("sleeep....")
            sleep(self.sleep_time)

            if self.stop_event.is_set():
                print("Process stopped")
                return


if __name__ == "__main__":
    stop_event = multiprocessing.Event()
    process = TakiProcess(stop_event)

    process.start()
    print("PID: ", process.pid)

    try:
        sleep(random() * 5)
        print("Processing...")
    except Exception as err:
        print("Exception: ", err)
    finally:
        stop_event.set()
        process.join()
