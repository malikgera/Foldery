from PyQt6.QtCore import QPoint, Qt, QUrl, pyqtSignal, QMimeData
from PyQt6.QtGui import QDrag, QDragEnterEvent, QDropEvent
from PyQt6.QtWidgets import QAbstractItemView, QListWidget


class DraggableIconList(QListWidget):
    filesDropped = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)

    def startDrag(self, supportedActions) -> None:
        item = self.currentItem()
        if not item:
            return
        icon_path = item.data(Qt.ItemDataRole.UserRole)
        if not icon_path:
            return
        drag = QDrag(self)
        mime = QMimeData()
        mime.setUrls([QUrl.fromLocalFile(icon_path)])
        mime.setData("application/x-foldery-icon", icon_path.encode("utf-8"))
        drag.setMimeData(mime)
        drag.setPixmap(item.icon().pixmap(64, 64))
        drag.setHotSpot(QPoint(32, 32))
        drag.exec(Qt.DropAction.CopyAction)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dropEvent(self, event: QDropEvent) -> None:
        if event.mimeData().hasUrls():
            paths = [url.toLocalFile() for url in event.mimeData().urls() if url.isLocalFile()]
            valid = [
                path
                for path in paths
                if path.lower().endswith((".ico", ".png", ".jpg", ".jpeg", ".icns"))
            ]
            if valid:
                self.filesDropped.emit(valid)
                event.acceptProposedAction()
                return
        super().dropEvent(event)
