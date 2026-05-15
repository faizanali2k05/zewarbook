from PyQt6.QtWidgets import QApplication


LUXURY_GOLD = "#D4AF37"
LUXURY_BG = "#111111"
LUXURY_SURFACE = "#1A1A1A"
LUXURY_SURFACE_ELEVATED = "#232323"
LUXURY_TEXT = "#F5F5F5"
LUXURY_TEXT_MUTED = "#CFCFCF"


def build_luxury_stylesheet() -> str:
    return f"""
QMainWindow, QWidget {{
    background-color: {LUXURY_BG};
    color: {LUXURY_TEXT};
    font-size: 13px;
}}

QLabel[heading="true"] {{
    color: {LUXURY_GOLD};
    font-size: 22px;
    font-weight: 700;
}}

QLabel[subtle="true"] {{
    color: {LUXURY_TEXT_MUTED};
}}

QFrame#authCard {{
    background-color: {LUXURY_SURFACE};
    border: 1px solid rgba(212, 175, 55, 0.45);
    border-radius: 16px;
}}

QFrame#sidebar {{
    background-color: #161616;
    border-left: 1px solid rgba(212, 175, 55, 0.45);
}}

QPushButton {{
    background-color: qlineargradient(
        x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 #2E2E2E,
        stop: 0.55 #222222,
        stop: 1 #181818
    );
    color: {LUXURY_TEXT};
    border: 1px solid rgba(212, 175, 55, 0.65);
    border-bottom: 3px solid #8D7320;
    border-radius: 10px;
    padding: 10px 18px;
    font-weight: 600;
}}

QPushButton:hover {{
    border-color: {LUXURY_GOLD};
    background-color: qlineargradient(
        x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 #3A3A3A,
        stop: 1 #252525
    );
}}

QPushButton:pressed {{
    padding-top: 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid #8D7320;
}}

QPushButton#primaryButton {{
    background-color: qlineargradient(
        x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 #E0BF57,
        stop: 1 #B5912D
    );
    color: #1A1A1A;
    border: 1px solid #E7C96F;
    border-bottom: 3px solid #8D7320;
}}

QPushButton#sidebarButton {{
    text-align: right;
    padding: 14px 18px;
    margin: 4px 10px;
    border-radius: 12px;
}}

QPushButton#sidebarButton[navActive="true"] {{
    background-color: #302812;
    border-color: {LUXURY_GOLD};
    color: #FFF6D8;
}}

QLineEdit, QComboBox, QDateEdit, QTextEdit {{
    background-color: {LUXURY_SURFACE_ELEVATED};
    color: {LUXURY_TEXT};
    border: 1px solid rgba(212, 175, 55, 0.75);
    border-radius: 10px;
    padding: 9px 12px;
    selection-background-color: rgba(212, 175, 55, 0.35);
}}

QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTextEdit:focus {{
    border: 1px solid {LUXURY_GOLD};
}}

QTableWidget {{
    background-color: {LUXURY_SURFACE};
    alternate-background-color: #202020;
    color: {LUXURY_TEXT};
    gridline-color: rgba(212, 175, 55, 0.25);
    border: 1px solid rgba(212, 175, 55, 0.5);
    border-radius: 10px;
}}

QHeaderView::section {{
    background-color: #272016;
    color: #F8EEC8;
    border: none;
    border-bottom: 1px solid rgba(212, 175, 55, 0.65);
    padding: 8px;
    font-weight: 700;
}}

QScrollBar:vertical {{
    background-color: #1A1A1A;
    width: 12px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background-color: rgba(212, 175, 55, 0.8);
    min-height: 26px;
    border-radius: 5px;
}}
"""


def apply_luxury_theme(app: QApplication) -> None:
    app.setStyleSheet(build_luxury_stylesheet())
