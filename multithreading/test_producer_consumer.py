"""
- producer-consumer problem https://en.wikipedia.org/wiki/Producer–consumer_problem
"""

from concurrent.futures import ThreadPoolExecutor
import logging
import random
import sys
import threading
import time
from os import getenv
from queue import Queue

import yappi
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


def to_palindrome(string: str):
    return f"{string}{string[::-1]}"


def is_palindrome(word: str):
    if len(word) // 2 == 0:
        return False

    time.sleep(0.1)
    return word == word[::-1]


# ================================================


def manual_producer(
    cond: threading.Condition,
    queue: Queue,
    stop_event: threading.Event,
    *,
    size: int = 1_000_000,
):
    logging.info("data_generator")

    for _ in range(size):
        value = ( 
            faker.ascii_email()
            if random.randint(0, 10) < 5
            else to_palindrome(faker.ascii_email())
        )  # fmt: off

        with cond:
            queue.put(value)
            logging.debug(f"Queue size: {queue.qsize()}")
            cond.notify_all()

        if stop_event.is_set() is True:
            break


def manual_consumer(
    cond: threading.Condition,
    queue: Queue,
    stop_event: threading.Event,
):
    logging.info("palindrome check")

    while True:
        with cond:
            while queue.empty():
                cond.wait()

            word = queue.get()
            if word is None:
                break

        if is_palindrome(word):
            logging.info(f"palindrome: {word}")
        else:
            logging.info(f"not a palindrome: {word}")

        if stop_event.is_set() is True:
            break


@yappi_wrap
def main_manual(execution_time: int = 60):
    logging.info("Starting...")
    condition = threading.Condition()
    stop_event = threading.Event()
    queue = Queue()
    local_data = threading.local()

    producers = [
        threading.Thread(
            name=f"producer_{i}",
            target=manual_producer,
            args=(condition, queue, stop_event),
        )
        for i in range(1)
    ]

    consumers = [
        threading.Thread(
            name=f"cons_{i}",
            target=manual_consumer,
            args=(condition, queue, stop_event),
        )
        for i in range(8)
    ]

    thread_group = producers + consumers
    for thread in thread_group:
        thread.start()

    try:
        time.sleep(execution_time)
    except KeyboardInterrupt:
        logging.info("Stopping...")
    finally:
        stop_event.set()
        for thread in thread_group:
            thread.join()


# ================================================


def pool_producer(queue: Queue, stop_event: threading.Event, *, size: int = 1_000_000):
    while size > 0:
        value = ( 
            faker.ascii_email()
            if random.randint(0, 10) < 5
            else to_palindrome(faker.ascii_email())
        )  # fmt: off
        size -= 1
        queue.put(value)

        if stop_event.is_set():
            break


def pool_consumer(pipeline: Queue, stop_event: threading.Event):
    while not pipeline.empty():
        message = pipeline.get()

        if message is None:
            break

        if is_palindrome(message):
            logging.info(f"palindrome: {message}")
        else:
            logging.info(f"not a palindrome: {message}")

        if stop_event.is_set():
            break

@yappi_wrap
def main_thread_pool(execution_time: int = 60):
    logging.info("Starting...")
    condition = threading.Condition()
    stop_event = threading.Event()
    queue = Queue()
    local_data = threading.local()

    pool = ThreadPoolExecutor(max_workers=8)
    pool.submit(pool_producer, queue, stop_event)
    pool.submit(pool_consumer, queue, stop_event)

    try:
        time.sleep(execution_time)
    except KeyboardInterrupt:
        logging.info("Stopping...")
    finally:
        stop_event.set()
        pool.shutdown()


if __name__ == "__main__":
    exec_time = 10
    print(f"Execution time: {exec_time} seconds, manual run...")
    main_manual(exec_time)
    print(f"Execution time: {exec_time} seconds, theard pool...")
    main_thread_pool(exec_time)
