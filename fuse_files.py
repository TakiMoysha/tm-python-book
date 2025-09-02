import logging
import os
import sys

from fuse import Operations
from PySide6.QtCore import QDir, QFileSystemWatcher, QTimer
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem
from PySide6.QtGui import QStandardItemModel
from PySide6.QtWidgets import QApplication, QListWidget
from PySide6.QtWidgets import QFileSystemModel
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QHeaderView
from PySide6.QtWidgets import QMainWindow
from PySide6.QtWidgets import QTreeView
from PySide6.QtWidgets import QWidget

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)

# ==========================================================================================
DEBUG = True

WORKING_DIR = os.getcwd()

VIRTUAL_FS_ROOT = os.path.join(WORKING_DIR, "tmp/mounted")
VIRTUAL_MOUNT_POINT = os.path.join(WORKING_DIR, "tmp/vfs")


# ==========================================================================================
def humanable_size(size) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]:
        if abs(size) < 1024.0:
            return f"{size:.1f}{unit}"
        size /= 1024.0
    return f"{size:.1f}YB"


# ==========================================================================================


class InMemoryFuse(Operations):
    def __init__(self):
        self.files = {}

    def readdir(self, path, fh):
        return [".", ".."] + list(self.files.keys())

    def getattr(self, path, fh=None):
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


class FSToVirtualFuse(Operations):
    def __init__(self, root):
        self.root = root

    def _full_path(self, partial):
        if partial.startswith("/"):
            partial = partial[1:]
        path = os.path.join(self.root, partial)
        return path

    def access(self, path, mode):
        full_path = self._full_path(path)
        if not os.access(full_path, mode):
            raise OSError(13, "Permission denied")

    def readdir(self, path, fh):
        full_path = self._full_path(path)
        dirents = [".", ".."]
        if os.path.isdir(full_path):
            dirents.extend(os.listdir(full_path))
        return dirents

    def getattr(self, path, fh=None):
        full_path = self._full_path(path)
        if not os.path.exists(full_path):
            raise OSError(2, "No such file or directory")

        st = os.lstat(full_path)
        return {
            "st_mode": st.st_mode,
            "st_ino": st.st_ino,
            "st_dev": st.st_dev,
            "st_nlink": st.st_nlink,
            "st_uid": st.st_uid,
            "st_gid": st.st_gid,
            "st_size": st.st_size,
            "st_atime": st.st_atime,
            "st_mtime": st.st_mtime,
            "st_ctime": st.st_ctime,
        }

    def open(self, path, flags):
        full_path = self._full_path(path)
        return os.open(full_path, flags)

    def read(self, path, size, offset, fh):
        os.lseek(fh, offset, 0)
        return os.read(fh, size)

    def readlink(self, path):
        pathname = os.readlink(self._full_path(path))
        if pathname.startswith("/"):
            return pathname
        return os.path.join(os.path.dirname(path), pathname)

    def statfs(self, path):
        full_path = self._full_path(path)
        stv = os.statvfs(full_path)
        return {
            "f_bsize": stv.f_bsize,
            "f_frsize": stv.f_frsize,
            "f_blocks": stv.f_blocks,
            "f_bfree": stv.f_bfree,
            "f_bavail": stv.f_bavail,
            "f_files": stv.f_files,
            "f_ffree": stv.f_ffree,
            "f_favail": stv.f_favail,
            "f_flag": stv.f_flag,
            "f_namemax": stv.f_namemax,
        }


# ==========================================================================================


class MainWindow(QMainWindow):
    def __init__(self, fuse):
        super().__init__()
        self.setWindowTitle("Demo FUSE - Virtual File System")
        self.resize(800, 600)

        # ========================= GUI
        # widget for real file system
        self.real_fs_model = QStandardItemModel()
        self.real_fs_model.setHorizontalHeaderLabels(["S", "File"])

        self.tree = QTreeView()
        self.tree.setModel(self.real_fs_model)
        self.tree.setSortingEnabled(True)
        self.tree.sortByColumn(1, Qt.SortOrder.AscendingOrder)
        self.tree.expandAll()
        self.tree.header().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        # widget for virtual file system
        self.fuse_model = QFileSystemModel()
        self.fuse_model.setRootPath(VIRTUAL_MOUNT_POINT)

        self.wd_fuse = QListWidget()
        self.wd_fuse.setWindowTitle("Enabled Files")

        # ==========================  Logic
        self.real_fs_model.dataChanged.connect(self.on_data_changed)
        self.populate_model(WORKING_DIR, self.real_fs_model.invisibleRootItem())

        self.watcher = QFileSystemWatcher()
        self.watcher.addPath(VIRTUAL_FS_ROOT)
        self.on_vfs_changed(VIRTUAL_FS_ROOT)

        # ========================== Compose
        root = QWidget()
        layout = QHBoxLayout(root)
        layout.addWidget(self.tree)
        layout.addWidget(self.wd_fuse)
        self.setCentralWidget(root)

    def populate_model(self, path, parent_item):
        dir_entry = QDir(path)
        filter_dirs = dir_entry.entryList(
            QDir.Filter.Dirs | QDir.Filter.NoDotAndDotDot,
            QDir.SortFlag.Name,
        )
        filter_files = dir_entry.entryInfoList(
            ["*.json", "*.txt", "*.py", "*.md"],
            QDir.Filter.Files | QDir.Filter.NoDotAndDotDot,
            QDir.SortFlag.Name,
        )

        for file_info in filter_files:
            # status checkbox
            checkbox_item = QStandardItem()
            checkbox_item.setCheckable(True)
            checkbox_item.setCheckState(Qt.CheckState.Unchecked)
            checkbox_item.setEditable(False)
            checkbox_item.setToolTip("Connect file to FUSE or not")

            # filename field
            file_item = QStandardItem(file_info.fileName())
            file_item.setEditable(False)
            file_item.setToolTip(file_info.absoluteFilePath())

            parent_item.appendRow([checkbox_item, file_item])

    def update_vfs_list(self):
        self.wd_fuse.clear()
        try:
            files = os.listdir(VIRTUAL_FS_ROOT)
            for f in sorted(files):
                full_path = os.path.join(VIRTUAL_FS_ROOT, f)
                if os.path.isfile(full_path):
                    self.wd_fuse.addItem(full_path)
                    size_str = humanable_size(os.path.getsize(full_path))
                    self.wd_fuse.addItem(f"{full_path} ({size_str})")
        except Exception as err:
            logging.error(f"Error while updating vfs list: {err}")

    def on_vfs_changed(self, path):
        QTimer.singleShot(100, self.update_vfs_list)

    def on_data_changed(self, top_left, bottom_right, roles):
        for row in range(top_left.row(), bottom_right.row() + 1):
            for column in range(top_left.column(), bottom_right.column() + 1):
                index = self.real_fs_model.index(row, column)
                item = self.real_fs_model.itemFromIndex(index)

                if item.isCheckable():
                    state = item.checkState()
                    parent = item.parent() or self.real_fs_model.invisibleRootItem()
                    file_item = parent.child(row, 1)
                    file_name = file_item.text() if file_item else "Unknown"

                    status = "Enable" if state == Qt.CheckState.Checked else "Ignore"
                    logging.info(f'on_data_changed: "{file_name}" {status}')


def run_cli():
    app = QApplication(sys.argv)

    # virtual_fuse = InMemoryFuse()
    virtual_fuse = FSToVirtualFuse(VIRTUAL_FS_ROOT)

    window = MainWindow(virtual_fuse)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    run_cli()
