import time
import threading

from queue import Queue

counter = 0
counter_lock = threading.Lock()


def produce(q):
    for i in range(10):
        item = f"item-{i}"
        print(f"Producing {item}")
        q.put(item)
        time.sleep(1)
    q.put(None)


def consume(q):
    while True:
        item = q.get()
        if item is None:
            break
        print(f"Consuming {item}")
        # time.sleep(1)
        q.task_done()


def main():
    q = Queue()
    producer_thread = threading.Thread(target=produce, args=(q,))
    consumer_thread = threading.Thread(target=consume, args=(q,))

    producer_thread.start()
    consumer_thread.start()

    producer_thread.join()
    consumer_thread.join()

    print(f"Finished: {''}")


if __name__ == "__main__":
    main()
