from PyQt6.QtGui import QPalette
from PyQt6.QtWidgets import QApplication

from ui.tokens import Tokens


def is_dark_mode() -> bool:
    app = QApplication.instance()
    if app is None:
        return False
    bg = app.palette().window().color()
    return (bg.red() + bg.green() + bg.blue()) / 3 < 128


def build_stylesheet(dark: bool) -> str:
    text = Tokens.TEXT_PRIMARY_DARK if dark else Tokens.TEXT_PRIMARY_LIGHT
    text_secondary = Tokens.TEXT_SECONDARY_DARK if dark else Tokens.TEXT_SECONDARY_LIGHT
    window_bg = "#1E1E20" if dark else "#EDEDF0"
    card_bg = Tokens.GLASS_DARK_SOLID if dark else Tokens.GLASS_LIGHT_SOLID
    border = Tokens.PANEL_BORDER_DARK if dark else Tokens.PANEL_BORDER_LIGHT
    input_bg = "rgba(255,255,255,18)" if dark else "rgba(0,0,0,6)"
    hover_bg = "rgba(255,255,255,14)" if dark else "rgba(0,0,0,5)"
    selected_bg = "rgba(10,132,255,55)" if dark else "rgba(10,132,255,35)"

    return f"""
        QMainWindow {{ background-color: {window_bg}; }}
        QWidget {{ color: {text}; font-family: '{Tokens.FONT_FAMILY}'; }}

        #appTitle {{ font-size: 19px; font-weight: 600; }}
        #panelTitle {{ font-size: 14px; font-weight: 600; color: {text}; }}
        #packLabel, #hintLabel {{ font-size: 11px; color: {text_secondary}; }}
        #statusText {{ font-size: 12px; color: {text_secondary}; }}

        QLineEdit {{
            background-color: {input_bg};
            border: 1px solid {border};
            border-radius: {Tokens.RADIUS_SM}px;
            padding: 8px 10px;
            selection-background-color: {Tokens.ACCENT};
        }}

        QTreeView, QListWidget {{
            background: transparent;
            border: none;
            outline: none;
        }}
        QTreeView::item, QListWidget::item {{
            border-radius: {Tokens.RADIUS_SM}px;
            padding: 4px;
        }}
        QTreeView::item:hover, QListWidget::item:hover {{
            background-color: {hover_bg};
        }}
        QTreeView::item:selected, QListWidget::item:selected {{
            background-color: {selected_bg};
            color: {text};
        }}

        QToolButton {{
            background-color: {input_bg};
            border: 1px solid {border};
            border-radius: {Tokens.RADIUS_SM}px;
            padding: 7px 14px;
            font-size: 12px;
        }}
        QToolButton:hover {{ background-color: {hover_bg}; }}
        QToolButton:pressed {{ background-color: {selected_bg}; }}

        QMenu {{
            background-color: {card_bg};
            border: 1px solid {border};
            border-radius: {Tokens.RADIUS_SM}px;
            padding: 4px;
        }}
        QMenu::item {{
            padding: 6px 14px;
            border-radius: 6px;
        }}
        QMenu::item:selected {{ background-color: {selected_bg}; }}

        #previewCard {{
            background-color: {card_bg};
            border: 1px solid {border};
            border-radius: {Tokens.RADIUS_MD}px;
        }}

        #primaryButton {{
            background-color: {Tokens.ACCENT};
            color: white;
            font-weight: 600;
            font-size: 13px;
            border: none;
            border-radius: {Tokens.RADIUS_SM}px;
        }}
        #primaryButton:hover {{ background-color: {Tokens.ACCENT_HOVER}; }}
        #primaryButton:pressed {{ background-color: {Tokens.ACCENT_PRESSED}; }}
        #primaryButton:disabled {{ background-color: {text_secondary}; }}

        #dangerButton {{
            background-color: transparent;
            color: {Tokens.DANGER};
            font-weight: 600;
            font-size: 13px;
            border: 1px solid {Tokens.DANGER};
            border-radius: {Tokens.RADIUS_SM}px;
        }}
        #dangerButton:hover {{
            background-color: {Tokens.DANGER};
            color: white;
        }}

        QStatusBar {{
            background: transparent;
            color: {text_secondary};
            font-size: 11px;
        }}
        QSplitter::handle {{ background: transparent; }}
        QScrollBar:vertical {{
            background: transparent;
            width: 10px;
            margin: 2px;
        }}
        QScrollBar::handle:vertical {{
            background: {hover_bg};
            border-radius: 5px;
            min-height: 24px;
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
    """
