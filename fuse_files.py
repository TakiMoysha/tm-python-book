import argparse
import logging
import os
import sys

from fuse import FUSE
from fuse import Operations
from PySide6.QtCore import QDir
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem
from PySide6.QtGui import QStandardItemModel
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QCheckBox
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QHeaderView
from PySide6.QtWidgets import QMainWindow
from PySide6.QtWidgets import QTableWidget
from PySide6.QtWidgets import QTableWidgetItem
from PySide6.QtWidgets import QTreeWidget
from PySide6.QtWidgets import QTreeWidgetItem
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)

# ==========================================================================================
WORKING_DIR = os.getcwd()

VIRTUAL_FS_ROOT = os.path.join(WORKING_DIR, "mounted")
VIRTUAL_MOUNT_POINT = os.path.join(WORKING_DIR, "vfs")
# ==========================================================================================


class VirtualFuse(Operations):
    def __init__(self):
        self.files = {}

    def readdir(self, path, fh):
        return [".", ".."] + list(self.files.keys())

    def getattr(self, path, fh=None):
        if not os.path.exists(path):
            raise OSError(2, f"No such file or directory: {path}")

        st = os.lstat(path)

        return dict(
            st_mode=st.st_mode,
            st_nlink=st.st_nlink,
            st_size=st.st_size,
            st_atime=st.st_atime,
            st_mtime=st.st_mtime,
            st_ctime=st.st_ctime,
        )

        if path == "/":
            return dict(st_mode=(0o755 | 0o040000), st_nlink=2)
        elif path[1:] in self.files:
            return dict(st_mode=(0o644 | 0o100000), st_size=len(self.files[path[1:]]), st_nlink=1)
        else:
            raise FileNotFoundError

    def open(self, path, flags):
        if path[1:] not in self.files:
            raise FileNotFoundError

    def read(self, path, size, offset, fh):
        data = self.files[path[1:]]
        return data[offset : offset + size]

    def write(self, path, data, offset, fh):
        if path[1:] not in self.files:
            self.files[path[1:]] = b""
        self.files[path[1:]] = self.files[path[1:]][:offset] + data + self.files[path[1:]][offset + len(data) :]
        return len(data)

    def create(self, path, mode):
        self.files[path[1:]] = b""
        return 0

    def unlink(self, path):
        if path[1:] in self.files:
            del self.files[path[1:]]
        else:
            raise FileNotFoundError


import os
import sys

from PySide6.QtCore import QFileInfo
from PySide6.QtCore import QModelIndex
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QFileSystemModel
from PySide6.QtWidgets import QMainWindow
from PySide6.QtWidgets import QTreeView
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Demo FUSE - Virtual File System")
        self.resize(800, 600)

        # Модель с двумя колонками: "Файл", "Подключать"
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["S", "File"])

        # Настройка дерева
        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setSortingEnabled(True)
        self.tree.sortByColumn(1, Qt.SortOrder.AscendingOrder)
        self.tree.expandAll()
        self.tree.header().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        # Сигнал изменения данных (например, при клике по чекбоксу)
        self.model.dataChanged.connect(self.on_data_changed)
        self.populate_model(WORKING_DIR, self.model.invisibleRootItem())

        root = QWidget()
        layout = QHBoxLayout(root)
        layout.addWidget(self.tree)
        self.setCentralWidget(root)

    def populate_model(self, path, parent_item):
        dir_entry = QDir(path)
        filter_dirs = dir_entry.entryList(QDir.Filter.Dirs | QDir.Filter.NoDotAndDotDot, QDir.SortFlag.Name)
        filter_files = dir_entry.entryInfoList(
            ["*.json", "*.txt", "*.py", "*.md"],
            QDir.Filter.Files | QDir.Filter.NoDotAndDotDot,
            QDir.SortFlag.Name,
        )

        for file_info in filter_files:
            # status checkbox
            checkbox_item = QStandardItem()
            checkbox_item.setCheckable(True)
            checkbox_item.setCheckState(Qt.CheckState.Checked)
            checkbox_item.setEditable(False)
            checkbox_item.setToolTip("Connect file to FUSE or not")

            # filename field
            file_item = QStandardItem(file_info.fileName())
            file_item.setEditable(False)
            file_item.setToolTip(file_info.absoluteFilePath())

            parent_item.appendRow([checkbox_item, file_item])

    def on_data_changed(self, top_left, bottom_right, roles):
        for row in range(top_left.row(), bottom_right.row() + 1):
            for column in range(top_left.column(), bottom_right.column() + 1):
                index = self.model.index(row, column)
                item = self.model.itemFromIndex(index)

                if item.isCheckable():
                    state = item.checkState()
                    parent = item.parent() or self.model.invisibleRootItem()
                    file_item = parent.child(row, 1)
                    file_name = file_item.text() if file_item else "Unknown"

                    status = "Enable" if state == Qt.CheckState.Checked else "Ignore"
                    logging.info(f'on_data_changed: "{file_name}" {status}')


def run_cli():
    # FUSE(SimpleFuse(), args.mountpoint, nothreads=True, foreground=True)

    app = QApplication(sys.argv)

    fuse_instance = VirtualFuse()

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    run_cli()
