import time
import threading

from concurrent.futures import ThreadPoolExecutor


default_vars = {"a": 1}


def task(n):
    print(f"Task {n} starting by thread {threading.current_thread().name}")
    # time.sleep(1)
    res = 0
    for i in range(999999):
        res = res + 1
        res = default_vars["a"] + res
    print(f"Task {n} finished")
    return res


def main():
    with ThreadPoolExecutor(max_workers=3) as executor:
        results = executor.map(task, range(10))

    print(f"{(x for x in results)}")
    print("Main thread finished.")


if __name__ == "__main__":
    main()
