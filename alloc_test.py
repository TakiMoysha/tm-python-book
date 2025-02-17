import time
import threading
import memray


def test_list_realloc():
    print("THREAD: ", hex(threading.get_ident()))

    def _test_list_realloc():
        value = "hello world!"
        _ = []
        ids = list()
        for i in range(10):
            value += str(i)
            _.append(value)
            ids.append(id(value))

        return ids

    start = time.time()
    ips = _test_list_realloc()
    print("list realloc: {}".format(time.time() - start))
    print([hex(n) for n in ips])


def test_list_resize():
    print("THREAD: ", hex(threading.get_ident()))

    def _test_list_resize():
        value = "hello world!"
        ids = list()
        for i in range(10):
            value += str(i)
            ids.append(id(value))

        return ids

    start = time.time()
    ips = _test_list_resize()
    print("list resize: {}".format(time.time() - start))
    print([hex(n) for n in ips])


def test_set():
    print("THREAD: ", hex(threading.get_ident()))

    def _test_set():
        value = "hello world!"
        ids = set()
        for i in range(10):
            value += str(i)
            ids.add(id(value))

        return ids

    start = time.time()
    ips = _test_set()
    print("set: {}".format(time.time() - start))
    print([hex(n) for n in ips])


if __name__ == "__main__":
    pool = (
        threading.Thread(target=test_list_realloc),
        threading.Thread(target=test_list_resize),
        threading.Thread(target=test_set),
    )

    list(t.start() for t in pool)
    list(t.join() for t in pool)
