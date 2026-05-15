import sys

from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.repositories.db import init_db
from src.services.auth_service import AuthService
from src.ui.main_window import MainWindow
from src.utils.qt_helpers import apply_urdu_defaults
from src.utils.styles import apply_luxury_theme


class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.auth = AuthService()
        self.auth.ensure_default_admin()
        self.setWindowTitle("جیولری انوینٹری سسٹم - لاگ اِن")

        root = QWidget()
        shell = QVBoxLayout()
        shell.setContentsMargins(48, 48, 48, 48)
        shell.setSpacing(20)

        title = QLabel("جیولری انوینٹری مینجمنٹ سسٹم")
        title.setProperty("heading", True)
        subtitle = QLabel("لگژری انوینٹری ڈیش بورڈ میں خوش آمدید")
        subtitle.setProperty("subtle", True)

        card = QFrame()
        card.setObjectName("authCard")
        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(30, 28, 30, 28)
        card_layout.setSpacing(16)

        form = QFormLayout()
        form.setVerticalSpacing(14)
        form.setHorizontalSpacing(12)
        self.username = QLineEdit()
        self.username.setPlaceholderText("اپنا صارف نام درج کریں")
        self.password = QLineEdit()
        self.password.setPlaceholderText("اپنا پاس ورڈ درج کریں")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        form.addRow("صارف نام", self.username)
        form.addRow("پاس ورڈ", self.password)

        btn = QPushButton("لاگ اِن")
        btn.setObjectName("primaryButton")
        btn.setMinimumHeight(44)
        btn.clicked.connect(self.login)

        card_layout.addLayout(form)
        card_layout.addWidget(btn)
        card.setLayout(card_layout)

        shell.addWidget(title)
        shell.addWidget(subtitle)
        shell.addWidget(card)
        shell.addStretch()

        root.setLayout(shell)
        self.setCentralWidget(root)

    def login(self):
        user = self.auth.login(self.username.text().strip(), self.password.text())
        if not user:
            QMessageBox.warning(self, "غلطی", "لاگ اِن ناکام")
            return
        self.main_window = MainWindow(user)
        self.main_window.show()
        self.close()


def run_login_app():
    init_db()
    app = QApplication(sys.argv)
    apply_urdu_defaults(app)
    apply_luxury_theme(app)
    window = LoginWindow()
    window.resize(640, 420)
    window.show()
    sys.exit(app.exec())
