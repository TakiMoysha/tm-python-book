import argparse
import hashlib
from concurrent.futures import ThreadPoolExecutor
import logging
import socket
import sys
import time
from os import getenv
from threading import Thread

logging.basicConfig(
    level=getenv("LOG_LEVEL", "INFO"),
    format="[%(asctime)s]: <%(threadName)s> %(message)s",
)


def run_server(host="127.0.0.1", port=33333, free_gil: bool = True):
    def _lifespan_gil_free():
        value = b"0"
        while True:
            # value = hashlib.sha256(value).digest()
            time.sleep(1)

    def _lifespan_gil_acquired():
        value = 0
        while True:
            value += 1
            value -= 1

    def _handle_client(sock):
        while True:
            received_data = sock.recv(4096)
            if not received_data:
                break
            sock.sendall(received_data)

        logging.info(f"Client disconnected: {sock.getpeername()}")
        sock.close()

    if free_gil:
        thr = Thread(target=_lifespan_gil_free).start()
    else:
        thr = Thread(target=_lifespan_gil_acquired).start()

    logging.info("Starting server...")
    sock = socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((host, port))
    sock.listen()
    while True:
        client_sock, addr = sock.accept()
        logging.info(f"Connection from {addr}")
        Thread(target=_handle_client, args=(client_sock,)).start()


def run_client(count: int = 1):
    requests_per_second = 0

    def _monitor():
        nonlocal requests_per_second
        while True:
            time.sleep(1)
            logging.info(f"{requests_per_second:.2f} reqs/sec")
            requests_per_second = 0

    def _connect(host="127.0.0.1", port=33333):
        nonlocal requests_per_second

        sock = socket.socket()
        sock.connect((host, port))

        while True:
            sock.sendall(b"0")
            sock.recv(4096)
            requests_per_second += 1

    with ThreadPoolExecutor(max_workers=count) as pool:
        pool.submit(_monitor)

        for _ in range(count):
            try:
                pool.submit(_connect)
            except ConnectionError:
                time.sleep(0.1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--server", action="store_true")
    parser.add_argument(
        "--free-gil",
        action="store_true",
        help="Use lifespan with free gil",
    )

    group.add_argument("--client", action="store_true")
    parser.add_argument(
        "--count",
        type=int,
        help="Number of clients to run",
        required="--client" in sys.argv,
    )
    args = parser.parse_args()

    if args.server:
        run_server(free_gil=args.free_gil)
    elif args.client:
        run_client(count=args.count)
