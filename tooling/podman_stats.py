import os
import socket
# import asyncio

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    _path: str = os.getenv("TM_PODMAN_SOCKET", f"/run/user/{os.getuid()}/podman/podman.sock")  # fmt: skip

    @property
    def path(self):
        return Path(self._path)


@lru_cache
def get_settings():
    return Settings()


def listen():
    path = get_settings().path
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

    if not os.path.exists(path):
        raise FileNotFoundError(f"Podman socket {get_settings().path} does not exist")

    sock.connect(str(path))

    try:
        while True:
            data = sock.recv(1024)
            if data is not None:
                print(data.decode("utf-8"))
    except KeyboardInterrupt:
        print("Interrupted...")
    finally:
        sock.close()


if __name__ == "__main__":
    listen()
