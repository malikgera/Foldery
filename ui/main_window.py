from __future__ import annotations

import os
from pathlib import Path

from PyQt6.QtCore import QDir, QEasingCurve, QPropertyAnimation, Qt, QSize
from PyQt6.QtGui import QFileSystemModel, QIcon, QPixmap, QAction
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QFileDialog,
    QFrame,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QSplitter,
    QStatusBar,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from config import IS_MACOS, IS_WINDOWS
from domain.errors import IconAssignError
from i18n.catalog import I18n
from services.assignment import AssignmentService, format_assign_error
from services.icon_pack import IconPack
from ui.theme import build_stylesheet, is_dark_mode
from ui.widgets.folder_tree import DropTreeView
from ui.widgets.glass_panel import GlassPanel
from ui.widgets.icon_gallery import DraggableIconList


class AnimatedToolButton(QToolButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._effect = QGraphicsOpacityEffect(self)
        self._effect.setOpacity(0.9)
        self.setGraphicsEffect(self._effect)
        self._anim = QPropertyAnimation(self._effect, b"opacity", self)
        self._anim.setDuration(160)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    def enterEvent(self, event):
        self._animate_to(1.0)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._animate_to(0.9)
        super().leaveEvent(event)

    def _animate_to(self, value: float) -> None:
        if self._anim.state() == QPropertyAnimation.State.Running:
            self._anim.stop()
        self._anim.setEndValue(value)
        self._anim.start()


class AnimatedToolButton(QToolButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._opacity_effect = QGraphicsOpacityEffect(self)
        self._opacity_effect.setOpacity(0.92)
        self.setGraphicsEffect(self._opacity_effect)
        self._anim = QPropertyAnimation(self._opacity_effect, b"opacity", self)
        self._anim.setDuration(180)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    def enterEvent(self, event):
        self._animate_to(1.0)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._animate_to(0.92)
        super().leaveEvent(event)

    def _animate_to(self, value: float) -> None:
        if self._anim.state() == QPropertyAnimation.State.Running:
            self._anim.stop()
        self._anim.setEndValue(value)
        self._anim.start()


class AnimatedPushButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._opacity_effect = QGraphicsOpacityEffect(self)
        self._opacity_effect.setOpacity(0.96)
        self.setGraphicsEffect(self._opacity_effect)
        self._anim = QPropertyAnimation(self._opacity_effect, b"opacity", self)
        self._anim.setDuration(180)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    def enterEvent(self, event):
        self._animate_to(1.0)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._animate_to(0.96)
        super().leaveEvent(event)

    def _animate_to(self, value: float) -> None:
        if self._anim.state() == QPropertyAnimation.State.Running:
            self._anim.stop()
        self._anim.setEndValue(value)
        self._anim.start()


class MainWindow(QMainWindow):
    def __init__(
        self,
        i18n: I18n,
        assignments: AssignmentService,
        pack: IconPack,
    ):
        super().__init__()
        self._i18n = i18n
        self._assignments = assignments
        self._pack = pack
        self.dark_mode = is_dark_mode()
        self.selected_icon: Path | None = None
        self.selected_folders: list[Path] = []

        self.setGeometry(100, 100, 1400, 820)
        self.setMinimumSize(1100, 650)

        self._build_ui()
        self._apply_native_backdrop()
        self._apply_theme()
        self._i18n.changed.connect(self.retranslate)
        self.retranslate()

        self.reload_gallery()
        self._populate_volumes()

    def t(self, key: str, **kwargs: object) -> str:
        return self._i18n.t(key, **kwargs)

    def retranslate(self) -> None:
        self.setWindowTitle(self.t("app.windowTitle"))
        self._title.setText(self.t("app.name"))
        self._pack_label.setText(self._pack_label_text())
        self._btn_pack.setText(self.t("toolbar.choosePack"))
        self._btn_theme.setToolTip(self.t("toolbar.theme"))
        self._btn_lang.setToolTip(self.t("toolbar.language"))
        self._btn_lang.setText(self._i18n.locale.upper())
        self._rebuild_lang_menu()
        self._tree_title.setText(self.t("tree.title"))
        self._tree_hint.setText("")
        self._tree_hint.hide()
        self._gallery_title.setText(self.t("gallery.title"))
        self._btn_refresh.setToolTip(self.t("gallery.refresh"))
        self._search.setPlaceholderText(self.t("gallery.search"))
        self._gallery_hint.setText(self.t("gallery.dropHint"))
        self._preview_title.setText(self.t("preview.title"))
        self._folder_path.setPlaceholderText(self.t("preview.placeholder"))
        self._btn_browse.setText(self.t("preview.browse"))
        self._btn_assign.setText(self.t("preview.assign"))
        self._btn_remove.setText(self.t("preview.remove"))
        self._refresh_multi_hint()
        if not self.selected_folders:
            self._current_name.setText(self.t("preview.noIcon"))

    def _pack_label_text(self) -> str:
        if self._pack.directory:
            name = self._pack.directory.name or str(self._pack.directory)
            return self.t("toolbar.pack.named", name=name)
        return self.t("toolbar.pack.none")

    def _rebuild_lang_menu(self) -> None:
        menu = QMenu(self)
        for locale in self._i18n.available():
            action = QAction(locale.native_name, self)
            action.setCheckable(True)
            action.setChecked(locale.code == self._i18n.locale)
            action.triggered.connect(lambda _=False, code=locale.code: self._i18n.set_locale(code))
            menu.addAction(action)
        self._btn_lang.setMenu(menu)

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(14)
        root.addWidget(self._build_toolbar())

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)
        splitter.setHandleWidth(14)
        splitter.addWidget(self._build_tree_panel())
        splitter.addWidget(self._build_gallery_panel())
        splitter.addWidget(self._build_preview_panel())
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 4)
        splitter.setStretchFactor(2, 3)
        splitter.setSizes([340, 460, 380])
        root.addWidget(splitter, 1)

        self.status = QStatusBar()
        self.setStatusBar(self.status)

    def _build_toolbar(self) -> QWidget:
        bar = QWidget()
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(4, 0, 4, 0)
        layout.setSpacing(10)

        self._title = QLabel()
        self._title.setObjectName("appTitle")
        layout.addWidget(self._title)
        layout.addStretch(1)

        self._pack_label = QLabel()
        self._pack_label.setObjectName("packLabel")
        layout.addWidget(self._pack_label)

        self._btn_pack = QToolButton()
        self._btn_pack.clicked.connect(self.choose_pack)
        layout.addWidget(self._btn_pack)

        self._btn_lang = QToolButton()
        self._btn_lang.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        layout.addWidget(self._btn_lang)

        self._btn_theme = QToolButton()
        self._btn_theme.setText("Theme")
        self._btn_theme.setIcon(QIcon("assets/icons/theme-icon.svg"))
        self._btn_theme.clicked.connect(self.toggle_theme)
        layout.addWidget(self._btn_theme)
        return bar

    def _build_tree_panel(self) -> QWidget:
        panel = GlassPanel(dark=self.dark_mode)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        header = QHBoxLayout()
        self._tree_title = QLabel()
        self._tree_title.setObjectName("panelTitle")
        header.addWidget(self._tree_title)
        header.addStretch(1)
        self._tree_hint = QLabel()
        self._tree_hint.setObjectName("hintLabel")
        header.addWidget(self._tree_hint)
        layout.addLayout(header)

        self.file_model = QFileSystemModel()
        self.file_model.setRootPath("")
        self.file_model.setFilter(
            QDir.Filter.AllDirs | QDir.Filter.NoDotAndDotDot | QDir.Filter.Drives
        )

        self.tree_view = DropTreeView()
        self.tree_view.setModel(self.file_model)
        self.tree_view.setHeaderHidden(True)
        for col in (1, 2, 3):
            self.tree_view.hideColumn(col)
        self.tree_view.setAnimated(False)
        self.tree_view.setUniformRowHeights(True)
        self.tree_view.setIndentation(16)
        self.tree_view.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.tree_view.selectionModel().selectionChanged.connect(self.on_tree_selection)
        self.tree_view.iconDroppedOnFolder.connect(self.on_icon_dropped_on_folder)
        self.tree_view.setObjectName("treeView")
        layout.addWidget(self.tree_view, 1)
        return panel

    def _build_gallery_panel(self) -> QWidget:
        panel = GlassPanel(dark=self.dark_mode)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        header = QHBoxLayout()
        self._gallery_title = QLabel()
        self._gallery_title.setObjectName("panelTitle")
        header.addWidget(self._gallery_title)
        header.addStretch(1)
        self._btn_refresh = QToolButton()
        self._btn_refresh.setText("Refresh")
        self._btn_refresh.setIcon(QIcon("assets/icons/refresh-icon.svg"))
        self._btn_refresh.clicked.connect(self.reload_gallery)
        header.addWidget(self._btn_refresh)
        layout.addLayout(header)

        self._search = QLineEdit()
        self._search.textChanged.connect(self.filter_gallery)
        layout.addWidget(self._search)

        self.icon_list = DraggableIconList()
        self.icon_list.setViewMode(QListWidget.ViewMode.IconMode)
        self.icon_list.setIconSize(QSize(84, 84))
        self.icon_list.setGridSize(QSize(108, 108))
        self.icon_list.setSpacing(6)
        self.icon_list.setUniformItemSizes(True)
        self.icon_list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.icon_list.setMovement(QListWidget.Movement.Static)
        self.icon_list.setObjectName("iconGallery")
        self.icon_list.itemClicked.connect(self.on_icon_selected)
        self.icon_list.itemDoubleClicked.connect(self.on_icon_double_clicked)
        self.icon_list.filesDropped.connect(self.on_icons_dropped_into_gallery)
        layout.addWidget(self.icon_list, 1)

        self._gallery_hint = QLabel()
        self._gallery_hint.setObjectName("hintLabel")
        self._gallery_hint.setWordWrap(True)
        layout.addWidget(self._gallery_hint)
        return panel

    def _build_preview_panel(self) -> QWidget:
        panel = GlassPanel(dark=self.dark_mode)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        self._preview_title = QLabel()
        self._preview_title.setObjectName("panelTitle")
        layout.addWidget(self._preview_title)

        path_row = QHBoxLayout()
        self._folder_path = QLineEdit()
        self._folder_path.setReadOnly(True)
        path_row.addWidget(self._folder_path)
        self._btn_browse = QToolButton()
        self._btn_browse.clicked.connect(self.browse_folder)
        path_row.addWidget(self._btn_browse)
        layout.addLayout(path_row)

        self._multi_hint = QLabel("")
        self._multi_hint.setObjectName("hintLabel")
        layout.addWidget(self._multi_hint)

        preview_card = QFrame()
        preview_card.setObjectName("previewCard")
        preview_layout = QVBoxLayout(preview_card)
        preview_layout.setContentsMargins(20, 24, 20, 24)

        self._current_preview = QLabel()
        self._current_preview.setFixedSize(140, 140)
        self._current_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_layout.addWidget(self._current_preview, alignment=Qt.AlignmentFlag.AlignCenter)

        self._current_name = QLabel()
        self._current_name.setObjectName("statusText")
        self._current_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._current_name.setWordWrap(True)
        preview_layout.addWidget(self._current_name)
        layout.addWidget(preview_card)
        layout.addStretch(1)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        self._btn_assign = QPushButton()
        self._btn_assign.setObjectName("primaryButton")
        self._btn_assign.setMinimumHeight(46)
        self._btn_assign.clicked.connect(self.assign_icon)
        btn_row.addWidget(self._btn_assign)

        self._btn_remove = QPushButton()
        self._btn_remove.setObjectName("dangerButton")
        self._btn_remove.setMinimumHeight(46)
        self._btn_remove.clicked.connect(self.remove_icon)
        btn_row.addWidget(self._btn_remove)
        layout.addLayout(btn_row)
        return panel

    def _apply_native_backdrop(self) -> None:
        if IS_WINDOWS:
            self._apply_mica()
        elif IS_MACOS:
            self._apply_vibrancy()

    def _apply_mica(self) -> None:
        try:
            import ctypes

            hwnd = int(self.winId())
            backdrop = ctypes.c_int(2)  # Mica
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, 38, ctypes.byref(backdrop), ctypes.sizeof(backdrop)
            )
            dark_flag = ctypes.c_int(1 if self.dark_mode else 0)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, 20, ctypes.byref(dark_flag), ctypes.sizeof(dark_flag)
            )
        except Exception:
            pass

    def _apply_vibrancy(self) -> None:
        try:
            import objc
            from AppKit import (
                NSVisualEffectBlendingMode,
                NSVisualEffectMaterial,
                NSVisualEffectView,
            )

            view = objc.objc_object(c_void_p=int(self.winId()))
            nsview = view.window()
            effect = NSVisualEffectView.alloc().initWithFrame_(nsview.contentView().bounds())
            effect.setMaterial_(NSVisualEffectMaterial.underWindowBackground)
            effect.setBlendingMode_(NSVisualEffectBlendingMode.behindWindow)
            effect.setState_(1)
            effect.setAutoresizingMask_(18)
            nsview.contentView().addSubview_positioned_relativeTo_(effect, 0, None)
        except Exception:
            pass

    def toggle_theme(self) -> None:
        self.dark_mode = not self.dark_mode
        self._apply_theme()
        self._apply_native_backdrop()

    def _apply_theme(self) -> None:
        for panel in self.findChildren(GlassPanel):
            panel.set_dark(self.dark_mode)
        self.setStyleSheet(build_stylesheet(self.dark_mode))

    def _populate_volumes(self) -> None:
        if IS_WINDOWS:
            self.tree_view.setRootIndex(self.file_model.index(""))
        else:
            self.tree_view.setRootIndex(self.file_model.index("/"))
            home = os.path.expanduser("~")
            self.tree_view.expand(self.file_model.index(home))

    def choose_pack(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, self.t("dialog.chooseIconsDir"))
        if folder:
            self._pack.set_directory(Path(folder))
            self._pack_label.setText(self._pack_label_text())
            self.reload_gallery()

    def reload_gallery(self) -> None:
        self.icon_list.clear()
        icons = self._pack.list_icons()
        if not self._pack.directory:
            self.status.showMessage(self.t("status.choosePack"), 5000)
            return
        try:
            for path in icons:
                item = QListWidgetItem(QIcon(str(path)), path.stem)
                item.setToolTip(path.name)
                item.setData(Qt.ItemDataRole.UserRole, str(path))
                self.icon_list.addItem(item)
            self.status.showMessage(self.t("status.loaded", n=len(icons)), 4000)
        except OSError as exc:
            QMessageBox.warning(self, self.t("dialog.error"), self.t("dialog.loadGallery", error=exc))

    def filter_gallery(self, text: str) -> None:
        needle = text.lower().strip()
        for i in range(self.icon_list.count()):
            item = self.icon_list.item(i)
            item.setHidden(needle not in item.text().lower())

    def on_icons_dropped_into_gallery(self, paths: list[str]) -> None:
        if not self._pack.directory:
            folder = QFileDialog.getExistingDirectory(self, self.t("dialog.choosePack"))
            if not folder:
                return
            self._pack.set_directory(Path(folder))
            self._pack_label.setText(self._pack_label_text())

        copied, errors = self._pack.add_files([Path(p) for p in paths])
        for path, exc in errors:
            QMessageBox.warning(
                self,
                self.t("dialog.error"),
                self.t("dialog.addFailed", path=path, error=exc),
            )
        if copied:
            self.reload_gallery()
            self.status.showMessage(self.t("status.added", n=copied), 4000)

    def on_icon_selected(self, item: QListWidgetItem) -> None:
        self.selected_icon = Path(item.data(Qt.ItemDataRole.UserRole))

    def on_icon_double_clicked(self, item: QListWidgetItem) -> None:
        self.selected_icon = Path(item.data(Qt.ItemDataRole.UserRole))
        if self.selected_folders:
            self.assign_icon()
        else:
            self.status.showMessage(self.t("status.pickFolder"), 4000)

    def on_tree_selection(self) -> None:
        indexes = self.tree_view.selectionModel().selectedIndexes()
        folders: list[Path] = []
        for index in indexes:
            if index.column() != 0:
                continue
            path = Path(self.file_model.filePath(index))
            if path.is_dir():
                folders.append(path)
        if not folders:
            return
        self.selected_folders = folders
        self._folder_path.setText(str(folders[0]))
        self._refresh_multi_hint()
        self.load_current_folder_icon()

    def _refresh_multi_hint(self) -> None:
        if len(self.selected_folders) > 1:
            self._multi_hint.setText(self.t("preview.multiHint", n=len(self.selected_folders)))
        else:
            self._multi_hint.setText("")

    def browse_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, self.t("dialog.chooseFolder"))
        if folder:
            self.selected_folders = [Path(folder)]
            self._folder_path.setText(folder)
            self._multi_hint.setText("")
            self.load_current_folder_icon()

    def on_icon_dropped_on_folder(self, folder_path: str, icon_path: str) -> None:
        folder = Path(folder_path)
        icon = Path(icon_path)
        errors = self._assignments.assign([folder], icon, pack_dir=self._pack.directory)
        if errors:
            self._show_assign_errors(errors)
            return
        self.selected_folders = [folder]
        self._folder_path.setText(str(folder))
        self._refresh_multi_hint()
        self.load_current_folder_icon()
        self.status.showMessage(self.t("status.assignedDrop", name=folder.name), 5000)

    def load_current_folder_icon(self) -> None:
        self._current_preview.clear()
        if not self.selected_folders:
            self._current_name.setText(self.t("preview.noIcon"))
            return

        folder = self.selected_folders[0]
        found = self._assignments.preview_path(folder, pack_dir=self._pack.directory)
        if self._assignments.supports_source_preview:
            if found and found.exists():
                pix = QPixmap(str(found)).scaled(
                    140,
                    140,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                self._current_preview.setPixmap(pix)
                self._current_name.setText(found.name)
                return
            self._current_name.setText(self.t("preview.noIcon"))
            return

        if found:
            self._current_name.setText(self.t("preview.customMac"))
        else:
            self._current_name.setText(self.t("preview.noIcon"))

    def assign_icon(self) -> None:
        if not self.selected_folders:
            QMessageBox.warning(self, self.t("dialog.notice"), self.t("dialog.needFolder"))
            return
        if not self.selected_icon:
            QMessageBox.warning(self, self.t("dialog.notice"), self.t("dialog.needIcon"))
            return

        errors = self._assignments.assign(
            self.selected_folders,
            self.selected_icon,
            pack_dir=self._pack.directory,
        )
        self.load_current_folder_icon()
        if errors:
            self._show_assign_errors(errors)
            return
        self.status.showMessage(
            self.t("status.assigned", name=self.selected_icon.name, n=len(self.selected_folders)),
            5000,
        )

    def remove_icon(self) -> None:
        if not self.selected_folders:
            return
        errors = self._assignments.remove(self.selected_folders)
        self.load_current_folder_icon()
        if errors:
            self._show_assign_errors(errors)
            return
        self.status.showMessage(self.t("status.removed"), 4000)

    def _show_assign_errors(self, errors: list[tuple[Path, IconAssignError]]) -> None:
        lines = [
            self.t(
                "dialog.assignFailed",
                path=path,
                error=format_assign_error(self._i18n, err),
            )
            for path, err in errors
        ]
        QMessageBox.critical(self, self.t("dialog.error"), "\n".join(lines))
