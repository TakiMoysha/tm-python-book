from contextvars import ContextVar
import sys
import time
import itertools
from typing import override
from weakref import WeakKeyDictionary
import PySide6
from PySide6.QtCore import QThread, Signal, QObject
from PySide6.QtWidgets import (
    QApplication,
    QLayout,
    QPushButton,
    QStackedLayout,
    QStackedWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

COUNT = ContextVar("COUNT", default=10_000_000)
items = []


class Worker(QThread):
    update = Signal(str)

    def run(self):
        name = self.objectName()
        n = COUNT.get()
        while n > 0:
            n -= 1
            items.append(name)
        self.update.emit(name)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("QThread Example")
        layout = QVBoxLayout()

        self.start_button = QPushButton("Start Counting")
        self.start_button.clicked.connect(self.start_threads)
        layout.addWidget(self.start_button)

        self.output = QTextEdit()
        layout.addWidget(self.output)

        self.setLayout(layout)

    def start_threads(self):
        self.output.clear()
        threads = []

        start_point = time.perf_counter()

        for i in range(3):
            worker = Worker()
            worker.setObjectName(f"Thread-{i + 1}")
            worker.update.connect(self.update_output)
            threads.append(worker)
            worker.start()

        for thread in threads:
            thread.wait()

        end_point = time.perf_counter()
        self.output.append(f"TIME: {end_point - start_point:.2f} seconds")
        self.output.append("Final counts:")
        for key, seq in itertools.groupby(items):
            self.output.append(f"{key}: {len(list(seq))}")

    def update_output(self, thread_name):
        self.output.append(f"{thread_name} finished counting.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
