import threading
import multiprocessing

from time import sleep


def numbers():
    for i in range(1, 50):
        print("Thread 1:", i)
        sleep(0.1)


def letters():
    for letter in ["a", "b", "c", "d", "e"] * 10:
        sleep(0.1)
        print("Thread 2:", letter)


# Create threads
worker_1 = threading.Thread(target=numbers)
worker_2 = threading.Thread(target=letters)
# or process
# worker_1 = multiprocessing.Process(target=numbers)
# worker_2 = multiprocessing.Process(target=letters)

# Start threads
worker_1.start()
worker_2.start()

# Wait for threads to finish
worker_1.join()
worker_2.join()

print("Example Complete.")
