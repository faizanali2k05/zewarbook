from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication

from config.settings import DEFAULT_FONT_FAMILY, DEFAULT_FONT_SIZE


def apply_urdu_defaults(app: QApplication) -> None:
    app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    app.setFont(QFont(DEFAULT_FONT_FAMILY, DEFAULT_FONT_SIZE))
