import contextvars
import threading
import time

x = 10
y = contextvars.ContextVar("y")


def increment(by):
    global x

    local_counter = x + by
    y.set(local_counter)

    time.sleep(0.2)

    x = local_counter
    print(f"{threading.current_thread().name} inc x {by}, x: {x}")


def main():
    # creating threads
    t1 = threading.Thread(target=increment, args=(5,))
    t2 = threading.Thread(target=increment, args=(10,))

    # starting the threads
    t1.start()
    t2.start()

    # waiting for the threads to complete
    t1.join()
    t2.join()

    print(f"The final value of x is {x}")


for i in range(10):
    main()
