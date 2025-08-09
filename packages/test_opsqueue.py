import concurrent.futures
import hashlib
import logging
import random
from argparse import ArgumentParser
from pathlib import Path
from string import ascii_lowercase

import pytest
from opsqueue.consumer import ConsumerClient
from opsqueue.consumer import Strategy
from opsqueue.producer import ProducerClient

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)


DEFAULT_QUEUE_ADDRESS = "localhost:3999"
DEFAULT_QUEUE_STORAGE = Path("/tmp/queue_storage")



def _as_fs(path):
    return "file://" + str(path)

def producer_start(queue_address: str, file_path: Path):
    producer = ProducerClient(queue_address, _as_fs(file_path.absolute()))
    while True:
        try:
            words = tuple([random.choice(ascii_lowercase).lower() * random.randint(16, 32) for _ in range(100_000)])
            logging.info(len(words))
            stream_of_capitalized_words = producer.run_submission(words, chunk_size=10000)
            logging.info(str(stream_of_capitalized_words))
        except KeyboardInterrupt:
            break

    pass

def consumer_start(queue_address: str, file_path: Path):
    consumer = ConsumerClient(queue_address, _as_fs(file_path))

    def _process(w):
        r = hashlib.sha256(w.encode()).hexdigest()
        logging.info(f"{w} -> {r}")
        return r

    consumer.run_each_op(lambda w: w.capitalize(), strategy=Strategy.Random())


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--consumer", action="store_true")
    parser.add_argument("--producer", action="store_true")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if args.consumer:
        consumer_start(DEFAULT_QUEUE_ADDRESS, DEFAULT_QUEUE_STORAGE)
    elif args.producer:
        producer_start(DEFAULT_QUEUE_ADDRESS, DEFAULT_QUEUE_STORAGE)
    else:
        parser.print_help()


@pytest.fixture(name="queue_storage", scope="package")
def temp_queue_storate():
    return DEFAULT_QUEUE_STORAGE


def test_consumer(queue_storage: Path):
    bus, file_path = "localhost:3999", queue_storage

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as p:
        p.submit(consumer_start, bus[0], file_path)
        p.submit(consumer_start, bus[0], file_path)
        p.submit(consumer_start, bus[0], file_path)
        p.submit(producer_start, bus[0], file_path)

    pass
