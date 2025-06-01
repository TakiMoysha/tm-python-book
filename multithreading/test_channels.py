import logging
import random
import threading
import time
from os import getenv
from queue import Queue

from faker import Faker

logging.basicConfig(
    level=getenv("LOG_LEVEL", "INFO"),
    format="%(threadName)s: %(message)s",
)

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


def producer(
    cond: threading.Condition,
    queue: Queue,
    stop_event: threading.Event,
    *,
    size: int = 1_000_000,
    seed: int = 0,
):
    random.seed(seed)
    logging.info("data_generator")

    for _ in range(size):
        value = ( 
            faker.ascii_email()
            if random.randint(0, 10) < 0
            else to_palindrome(faker.ascii_email())
        )  # fmt: off

        with cond:
            queue.put(value)
            logging.debug(f"Queue size: {queue.qsize()}")
            cond.notify_all()

        if stop_event.is_set() is True:
            break


# ================================================
def consumer(
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


# ================================================
# ================================================
# ================================================
# ================================================


def main():
    logging.info("Starting...")
    condition = threading.Condition()
    stop_event = threading.Event()
    queue = Queue()
    local_data = threading.local()

    producers = [
        threading.Thread(
            name=f"producer_{i}",
            target=producer,
            args=(condition, queue, stop_event),
        )
        for i in range(1)
    ]

    consumers = [
        threading.Thread(
            name=f"cons_{i}",
            target=consumer,
            args=(condition, queue, stop_event),
        )
        for i in range(8)
    ]

    thread_group = producers + consumers
    for thread in thread_group:
        thread.start()

    # fmt: off
    # for thread in consumers: thread.start() # noqa
    # for prod in producers: prod.start() # noqa
    # fmt: on

    # time.sleep(10)
    try:
        for thread in thread_group:
            thread.join()
    except KeyboardInterrupt:
        logging.info("Stopping...")
        stop_event.set()


if __name__ == "__main__":
    main()
