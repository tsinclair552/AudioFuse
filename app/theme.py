from PySide6.QtWidgets import QGraphicsDropShadowEffect, QWidget
from PySide6.QtGui import QColor


CANVAS = "#ffffff"
PARCHMENT = "#f5f5f7"
INK = "#1d1d1f"
INK_MUTED = "#7a7a7a"
PRIMARY = "#0066cc"
PRIMARY_HOVER = "#0055aa"
PRIMARY_PRESSED = "#004488"
PRIMARY_DISABLED = "#b3d4f0"
HAIRLINE = "#e0e0e0"
ERROR_RED = "#ff3b30"


def product_shadow(parent: QWidget) -> QGraphicsDropShadowEffect:
    effect = QGraphicsDropShadowEffect(parent)
    effect.setBlurRadius(30)
    effect.setOffset(3, 5)
    effect.setColor(QColor(0, 0, 0, 55))
    return effect


MAIN_WINDOW_STYLE = f"""
    QMainWindow {{
        background-color: {CANVAS};
    }}
"""

PANEL_STYLE = f"""
    AudioPanel {{
        background-color: {PARCHMENT};
        border: 1px solid {HAIRLINE};
        border-radius: 18px;
    }}
    AudioPanel QLabel {{
        background: transparent;
        border: none;
    }}
"""

GAP_BUTTON_STYLE = f"""
    QPushButton {{
        background: transparent;
        border: 1px solid {PRIMARY};
        color: {PRIMARY};
        border-radius: 9999px;
        padding: 8px 22px;
        font-size: 14px;
    }}
    QPushButton:hover {{
        background: {PRIMARY};
        color: white;
    }}
    QPushButton:pressed {{
        background: {PRIMARY_PRESSED};
        color: white;
    }}
    QPushButton:checked {{
        background: {PRIMARY};
        color: white;
    }}
    QPushButton:checked:hover {{
        background: {PRIMARY_HOVER};
        color: white;
    }}
"""

ACTION_BUTTON_STYLE = f"""
    QPushButton {{
        background-color: {PRIMARY};
        color: white;
        border: none;
        border-radius: 9999px;
        padding: 8px 22px;
        font-size: 14px;
    }}
    QPushButton:hover {{
        background-color: {PRIMARY_HOVER};
    }}
    QPushButton:pressed {{
        background-color: {PRIMARY_PRESSED};
    }}
    QPushButton:disabled {{
        background-color: {PRIMARY_DISABLED};
        color: white;
    }}
"""
