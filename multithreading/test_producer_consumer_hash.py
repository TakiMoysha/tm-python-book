""""""

from concurrent.futures import ThreadPoolExecutor
import hashlib
import logging
import random
import sys
import yappi
import threading
import time
from os import getenv
from queue import Queue

from faker import Faker

logging.basicConfig(
    level=getenv("LOG_LEVEL", "INFO"),
    format="[%(asctime)s]: <%(threadName)s> %(message)s",
)


# ================================================
def yappi_wrap(fn):
    def wrapper(*args, **kwargs):
        t1 = time.perf_counter(), time.process_time()
        yappi.set_clock_type("cpu")
        yappi.start()

        try:
            fn(*args, **kwargs)
        except Exception:
            pass
        finally:
            yappi.stop()
            t2 = time.perf_counter(), time.process_time()
            yappi.get_func_stats().print_all()
            yappi.get_thread_stats().print_all()

            logging.info(f"TIME: {t2[0] - t1[0]:.2f} seconds")
            logging.info(f"CPU TIME: {t2[1] - t1[1]:.2f} seconds")

    return wrapper


# ================================================
faker = Faker()


def hash_message(msg: str):
    return hashlib.sha256(msg.encode()).hexdigest()


# ================================================


def producer(queue: Queue, stop_event: threading.Event, *, size: int = 1_000_000):
    while size > 0:
        value = faker.sha256()
        size -= 1
        queue.put(value)

        if stop_event.is_set():
            break


def consumer(queue: Queue, stop_event: threading.Event):
    while not queue.empty():
        message = queue.get()

        if message is None:
            break

        res = hash_message(message)
        logging.info(f"hashing: {message} -> {res}")

        if stop_event.is_set():
            break

@yappi_wrap
def main(execution_time: int = 60):
    logging.info("Starting...")
    condition = threading.Condition()
    stop_event = threading.Event()
    queue = Queue()
    local_data = threading.local()

    # pool = ThreadPoolExecutor(max_workers=8)
    with ThreadPoolExecutor(max_workers=8) as pool:
        pool.submit(producer, queue, stop_event)
        pool.submit(consumer, queue, stop_event)
        pool.submit(consumer, queue, stop_event)
        pool.submit(consumer, queue, stop_event)
        pool.submit(consumer, queue, stop_event)

        try:
            time.sleep(execution_time)
        except KeyboardInterrupt:
            logging.info("Stopping...")
            stop_event.set()
        finally:
            pool.shutdown()


if __name__ == "__main__":
    exec_time = 10
    main(exec_time)
