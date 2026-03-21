import argparse
from collections import deque
from time import perf_counter


# ===========================================================
# ===========================================================


def deque_left_insert():
    parser = argparse.ArgumentParser()
    parser.add_argument("times", type=int, default=10_000)

    args = parser.parse_args()
    times = args.times

    # =======================================================
    a_list = []
    a_append_list = []
    a_deque = deque()

    def average_time(func, times):
        total = 0.0
        for i in range(times):
            start = perf_counter()
            func(i)
            total += (perf_counter() - start) * 1e9
        return total / times

    list_time = average_time(lambda i: a_list.insert(0, i), times)
    append_list_time = average_time(lambda i: a_append_list.append(0), times)
    deque_time = average_time(lambda i: a_deque.appendleft(i), times)
    gain = list_time / deque_time

    print(f"list.insert()      {list_time:.6} ns")
    print(f"list.append()      {append_list_time:.6} ns")
    print(f"deque.appendleft() {deque_time:.6} ns  ({gain:.6}x faster)")


# ===========================================================
# ===========================================================


def deque_random_access():
    parser = argparse.ArgumentParser()
    parser.add_argument("times", type=int, default=10_000)

    args = parser.parse_args()
    times = args.times

    # =======================================================

    a_list = [1] * times
    a_deque = deque(a_list)

    def average_time(func, times):
        total = 0.0
        for _ in range(times):
            start = perf_counter()
            func()
            total += (perf_counter() - start) * 1e6
        return total / times

    def time_it(sequence):
        middle = len(sequence) // 2
        sequence.insert(middle, "middle")
        sequence[middle]
        sequence.remove("middle")
        del sequence[middle]

    list_time = average_time(lambda: time_it(a_list), times)
    deque_time = average_time(lambda: time_it(a_deque), times)
    gain = deque_time / list_time

    print(f"list  {list_time:.6} μs ({gain:.6}x faster)")
    print(f"deque {deque_time:.6} μs")
