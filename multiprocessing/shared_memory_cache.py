from dataclasses import dataclass, field
from functools import lru_cache
from multiprocessing import shared_memory
import os


@dataclass
class Config:
    name: str = field(default_factory=lambda: os.getenv("TM_NAME", "shared_cache"))
    size: int = field(default_factory=lambda: 1024 * 1024)


config = Config()

class SharedMemryCache:
    def __init__(self) -> None:
        self.shm = shared_memory.SharedMemory(create=True, name=config.name, size=config.size)
