import pickle
import multiprocessing

from time import sleep
from random import random
from multiprocessing import Pipe, Queue, Process


class DemoObject:
    def __init__(self, *args, **kwargs):
        self.value = args

def handler():
    pass


def handler_with_pipe(rec, send):
    value = random()
    data = DemoObject(*[value, ])
    sleep(value)
    print("Generated value: ", value, flush=True)
    send.send(data)

def handler_with_queue(queue):
    value = random()
    data = DemoObject(*[value, ])
    sleep(value)
    print("Generated value: ", value, flush=True)
    queue.put(data)

if __name__ == "__main__":
    process = Process(target=handler)
    try:
        process.start()
        print("PID: ", process.pid)
    except Exception as err:
        print("Exception: ", err)
    finally:
        process.join()
        process.close()

    rec, send = Pipe()
    process_with_pipe = Process(target=handler_with_pipe, args=(rec, send))
    try:
        process_with_pipe.start()
        print("Value: ", rec.recv().value)
    except Exception as err:
        print("Exception: ", err)
    finally:
        process_with_pipe.join()
        process_with_pipe.close()


    queue = Queue()
    process_with_queue = Process(target=handler_with_queue, args=(queue, ))
    try:
        process_with_queue.start()
        print("Value: ", queue.get().value)
    except Exception as err:
        print("Exception: ", err)
    finally:
        process_with_queue.join()
        process_with_queue.close()




