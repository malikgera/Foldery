import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import QApplication

from config import APP_NAME, ORG_NAME, IS_MACOS, IS_WINDOWS
from i18n.catalog import I18n
from platforms import create_backend
from services.assignment import AssignmentService
from services.icon_pack import IconPack
from ui.main_window import MainWindow


def main() -> None:
    app = QApplication(sys.argv)
    icon_path = BASE_DIR / "icon.ico"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    app.setApplicationName(APP_NAME)
    app.setOrganizationName(ORG_NAME)

    font = QFont()
    if IS_WINDOWS:
        font.setFamily("Segoe UI")
    elif IS_MACOS:
        font.setFamilies(["SF Pro Display", "SF Pro Text", "Helvetica Neue", "Arial"])
    else:
        font.setFamily("Segoe UI")
    font.setStyleStrategy(QFont.StyleStrategy.PreferMatch)
    app.setFont(font)

    window = MainWindow(
        i18n=I18n(),
        assignments=AssignmentService(create_backend()),
        pack=IconPack.from_env(),
    )
    if icon_path.exists():
        window.setWindowIcon(QIcon(str(icon_path)))
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
