import threading
import multiprocessing

from time import sleep

from multithreading.utils import cpu_bound_task

# Create threads
# worker_1 = threading.Thread(target=cpu_bound_task)
# worker_2 = threading.Thread(target=cpu_bound_task)
# or process
worker_1 = multiprocessing.Process(target=cpu_bound_task)
worker_2 = multiprocessing.Process(target=cpu_bound_task)

# Start threads
worker_1.start()
worker_2.start()

# Wait for threads to finish
worker_1.join()
worker_2.join()

print("Example Complete.")
