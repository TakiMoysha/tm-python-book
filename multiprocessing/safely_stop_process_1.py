import os
import signal
import multiprocessing

from time import sleep
from random import random
from multiprocessing import Process, Event


class SignalException(Exception): ...


def signal_handler(signum, frame):
    raise SignalException("Signal Exception: ", signum, frame)


class TakiProcess(Process):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stop_event = Event()
        self.sleep_time = 0

    def run(self):
        self.sleep_time = random()
        while True:
            print("sleeep....", flush=True)
            sleep(self.sleep_time)

            if self.stop_event.is_set():
                print("Process stopped")
                return


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, signal_handler)
    process = TakiProcess()

    print("MAIN.PID: ", os.getpid())
    process.start()
    print("PID: ", process.pid)

    try:
        print("Processing...")
        sleep(random() * 10)
    except SignalException as err:
        process.stop_event.set()
        print("Signal Exception: ", err)
    except KeyboardInterrupt:
        print("User Interrupted")
    except Exception as err:
        print("Error occured : ", err)
    finally:
        process.stop_event.set()
        process.join()
