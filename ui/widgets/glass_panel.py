from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QFrame, QGraphicsDropShadowEffect

from ui.tokens import Tokens


class GlassPanel(QFrame):
    def __init__(self, dark: bool = False, radius: int = Tokens.RADIUS_LG, parent=None):
        super().__init__(parent)
        self._dark = dark
        self._radius = radius
        self.setObjectName("glassPanel")
        self._apply_style()
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(28)
        shadow.setOffset(0, 6)
        shadow.setColor(QColor(0, 0, 0, 60 if dark else 35))
        self.setGraphicsEffect(shadow)

    def _apply_style(self) -> None:
        bg = Tokens.GLASS_DARK if self._dark else Tokens.GLASS_LIGHT
        border = Tokens.PANEL_BORDER_DARK if self._dark else Tokens.PANEL_BORDER_LIGHT
        self.setStyleSheet(f"""
            #glassPanel {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: {self._radius}px;
            }}
        """)

    def set_dark(self, dark: bool) -> None:
        self._dark = dark
        self._apply_style()
