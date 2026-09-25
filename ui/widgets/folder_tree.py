import os

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent
from PyQt6.QtWidgets import QTreeView


class DropTreeView(QTreeView):
    iconDroppedOnFolder = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasFormat("application/x-foldery-icon") or event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event) -> None:
        index = self.indexAt(event.position().toPoint())
        if index.isValid():
            self.setCurrentIndex(index)
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent) -> None:
        index = self.indexAt(event.position().toPoint())
        if not index.isValid():
            event.ignore()
            return

        folder_path = self.model().filePath(index)
        if not os.path.isdir(folder_path):
            event.ignore()
            return

        icon_path = None
        mime = event.mimeData()
        if mime.hasFormat("application/x-foldery-icon"):
            icon_path = bytes(mime.data("application/x-foldery-icon")).decode("utf-8")
        elif mime.hasUrls():
            urls = mime.urls()
            if urls and urls[0].isLocalFile():
                icon_path = urls[0].toLocalFile()

        if icon_path:
            self.iconDroppedOnFolder.emit(folder_path, icon_path)
            event.acceptProposedAction()
        else:
            event.ignore()
