import time
import itertools

from threading import Thread, current_thread
from multiprocessing import pool

COUNT = 10_000_000

items = []


def count(n):
    name = current_thread().name
    while n > 0:
        n -= 1
        items.append(name)


threads = [Thread(target=count, args=(COUNT,)) for _ in range(3)]

start_point = time.perf_counter()
list(map(lambda t: t.start(), threads))
list(map(lambda t: t.join(), threads))
end_point = time.perf_counter()


# Output a condensed trace showing thread scheduling
for key, seq in itertools.groupby(items):
    print("%s %s" % (key, len(list(seq))))

print("TIME:", end_point - start_point)
