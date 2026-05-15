"""Main jewelry inventory window — Urdu RTL, light theme, top-tab navigation.

Layout mirrors the reference screenshots:
    [ top bar: tabs (روزنامچہ | ادھار | لیب)  |  rate fields  ]
    [ weight calc | customer mgmt + nقد panel | ادھار panel    ]
    [ purity table (Local/Copper/Standard/Silver/PureSilver)    ]
    [ 4 receipt panels: وصولی | لیب | ادھار کی | نقدی کی        ]
    [ footer totals: کیش | تیزابی سونا | پرچون                  ]
"""
from datetime import datetime

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from src.domain import purity as purity_module
from src.domain import units
from src.services.backup_service import BackupService
from src.services.customer_service import CustomerService
from src.services.report_service import ReportService

GOLD = "#1f6f3e"  # green for action buttons in screenshots
LABEL_BG = "#e8e8e8"
FIELD_GREEN = "#e7f4d8"
FIELD_YELLOW = "#ffffd2"
FIELD_GRAY = "#d9d9d9"
HEADER_GRAY = "#8b8b8b"
TEXT_DARK = "#111111"
URDU_FONT = "Noto Nastaliq Urdu"


def _money(value: float) -> str:
    return f"{value:,.2f}" if value else "-"


def _num(value: float, decimals: int = 4) -> str:
    if not value:
        return "-"
    return f"{value:.{decimals}f}".rstrip("0").rstrip(".")


class _ReadField(QLineEdit):
    """Compact read-only display field with right-aligned text."""

    def __init__(self, text: str = "-", parent=None) -> None:
        super().__init__(text, parent)
        self.setReadOnly(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(
            "QLineEdit{background:#ffffff;border:1px solid #888;padding:2px 6px;color:#111;}"
        )


class _InputField(QLineEdit):
    def __init__(self, placeholder: str = "", parent=None) -> None:
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(
            "QLineEdit{background:#ffffff;border:1px solid #888;padding:4px 8px;color:#111;}"
            "QLineEdit:focus{border:1px solid #1f6f3e;}"
        )


class MainWindow(QMainWindow):
    def __init__(self, user) -> None:
        super().__init__()
        self.user = user
        self.customer_svc = CustomerService()
        self.backup_svc = BackupService()
        self.report_svc = ReportService()

        self._current_customer_id: int | None = None
        self._customer_cache: list = []
        self._customer_index: int = -1
        self._clock_frozen = False

        self.setWindowTitle("جیولری انوینٹری مینجمنٹ سسٹم")
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setFont(QFont(URDU_FONT, 10))
        self.setStyleSheet(f"QMainWindow{{background:{LABEL_BG};}}")

        root = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        layout.addWidget(self._build_top_tab_bar())
        layout.addWidget(self._build_middle_row(), 0)
        layout.addWidget(self._build_purity_table_frame(), 0)
        layout.addWidget(self._build_receipt_panels_row(), 1)
        layout.addWidget(self._build_footer_totals())

        root.setLayout(layout)
        self.setCentralWidget(root)
        self.setMinimumSize(1280, 800)
        self.showMaximized()

        self._init_clock()
        self._wire_rate_signals()
        self._wire_weight_signals()
        self._refresh_totals()
        self._set_receipt_no(self.customer_svc.next_receipt_no())

    # ─────────────────────────────────────────────────────────────────
    # Layout builders
    # ─────────────────────────────────────────────────────────────────
    def _build_top_tab_bar(self) -> QFrame:
        bar = QFrame()
        bar.setStyleSheet(
            f"QFrame{{background:{LABEL_BG};border-bottom:1px solid #999;}}"
        )
        row = QHBoxLayout()
        row.setContentsMargins(6, 6, 6, 6)
        row.setSpacing(10)

        self.close_btn = QPushButton("X")
        self.close_btn.setFixedSize(28, 28)
        self.close_btn.setStyleSheet(
            "QPushButton{background:#cccccc;border:1px solid #777;font-weight:bold;}"
        )
        self.close_btn.clicked.connect(self.close)

        # Date
        row.addWidget(self.close_btn)
        row.addWidget(QLabel("تاریخ"))
        self.header_date = _InputField()
        self.header_date.setFixedWidth(110)
        self.header_date.setText(datetime.now().strftime("%d/%m/%Y"))
        row.addWidget(self.header_date)

        # Rates
        row.addWidget(QLabel("ریٹ تیزابی فی تولہ"))
        self.rate_per_tola = _InputField()
        self.rate_per_tola.setFixedWidth(90)
        row.addWidget(self.rate_per_tola)

        row.addWidget(QLabel("ریٹ تیزابی فی گرام"))
        self.rate_per_gram = _ReadField()
        self.rate_per_gram.setFixedWidth(90)
        row.addWidget(self.rate_per_gram)

        row.addWidget(QLabel("پرچی چارجز"))
        self.parchi_charge = _InputField()
        self.parchi_charge.setFixedWidth(70)
        self.parchi_charge.setText("100")
        row.addWidget(self.parchi_charge)

        row.addWidget(QLabel("فی گرام چارجز"))
        self.per_gram_charge = _InputField()
        self.per_gram_charge.setFixedWidth(70)
        self.per_gram_charge.setText("80")
        row.addWidget(self.per_gram_charge)

        row.addStretch()

        # Top-right tabs
        self.tab_roznamcha = QPushButton("روزنامچہ")
        self.tab_udhaar = QPushButton("ادھار")
        self.tab_lab = QPushButton("لیب")
        for b in (self.tab_roznamcha, self.tab_udhaar, self.tab_lab):
            b.setMinimumWidth(80)
            b.setMinimumHeight(28)
            b.setStyleSheet(
                "QPushButton{background:#e8e8e8;border:1px solid #888;padding:4px 14px;"
                f"font-family:'{URDU_FONT}';font-weight:bold;}}"
                "QPushButton:hover{background:#d4d4d4;}"
            )
            row.addWidget(b)

        self.tab_roznamcha.clicked.connect(self._open_roznamcha)
        self.tab_udhaar.clicked.connect(self._open_udhaar_dialog)
        self.tab_lab.clicked.connect(self._open_lab_dialog)

        bar.setLayout(row)
        return bar

    def _build_middle_row(self) -> QFrame:
        frame = QFrame()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        layout.addWidget(self._build_weight_calculator(), 1)
        layout.addWidget(self._build_customer_panel(), 1)
        layout.addWidget(self._build_naqad_panel(), 1)
        layout.addWidget(self._build_udhaar_panel(), 1)
        frame.setLayout(layout)
        return frame

    def _build_weight_calculator(self) -> QFrame:
        f = QFrame()
        f.setStyleSheet("QFrame{background:#ffffff;border:1px solid #aaa;}")
        grid = QGridLayout()
        grid.setContentsMargins(6, 6, 6, 6)
        grid.setHorizontalSpacing(6)
        grid.setVerticalSpacing(4)

        for col, header in enumerate(["(گرام)", "تولہ", "ماشہ", "رتی"]):
            lbl = QLabel(header)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            grid.addWidget(lbl, 0, col + 1)

        grid.addWidget(QLabel("وزن کنڈے پر"), 1, 0)
        self.air_grams = _InputField()
        self.air_grams.setStyleSheet(
            f"QLineEdit{{background:{FIELD_GREEN};border:1px solid #888;padding:3px;}}"
        )
        self.air_tola = _ReadField()
        self.air_masha = _ReadField()
        self.air_rati = _ReadField()
        for col, w in enumerate([self.air_grams, self.air_tola, self.air_masha, self.air_rati]):
            grid.addWidget(w, 1, col + 1)

        grid.addWidget(QLabel("وزن پانی میں"), 2, 0)
        self.water_grams = _InputField()
        self.water_grams.setStyleSheet(
            f"QLineEdit{{background:{FIELD_GREEN};border:1px solid #888;padding:3px;}}"
        )
        self.water_tola = _ReadField()
        self.water_masha = _ReadField()
        self.water_rati = _ReadField()
        for col, w in enumerate([self.water_grams, self.water_tola, self.water_masha, self.water_rati]):
            grid.addWidget(w, 2, col + 1)

        f.setLayout(grid)
        return f

    def _build_customer_panel(self) -> QFrame:
        f = QFrame()
        f.setStyleSheet("QFrame{background:#ffffff;border:1px solid #aaa;}")
        grid = QGridLayout()
        grid.setContentsMargins(6, 6, 6, 6)
        grid.setHorizontalSpacing(6)
        grid.setVerticalSpacing(4)

        self.btn_plus = QPushButton("+")
        self.btn_plus.setFixedWidth(28)
        self.btn_plus.clicked.connect(self._on_clear_form)

        self.field_name = QComboBox()
        self.field_name.setEditable(True)
        self.field_name.setStyleSheet(f"QComboBox{{background:{FIELD_GREEN};border:1px solid #888;}}")
        self.btn_new = QPushButton("New")
        self.btn_new.setStyleSheet(
            f"QPushButton{{color:#cc0000;font-weight:bold;background:transparent;border:none;}}"
        )
        self.btn_new.clicked.connect(self._on_new_customer)
        grid.addWidget(self.btn_plus, 0, 0)
        grid.addWidget(self.field_name, 0, 1)
        grid.addWidget(QLabel("نام"), 0, 2)
        grid.addWidget(self.btn_new, 0, 3)

        self.field_mobile = QComboBox()
        self.field_mobile.setEditable(True)
        self.field_mobile.setStyleSheet(f"QComboBox{{background:{FIELD_GREEN};border:1px solid #888;}}")
        self.btn_find = QPushButton("Find")
        self.btn_find.setStyleSheet(
            f"QPushButton{{color:#cc0000;font-weight:bold;background:transparent;border:none;}}"
        )
        self.btn_find.clicked.connect(self._on_find_customer)
        grid.addWidget(self.field_mobile, 1, 1)
        grid.addWidget(QLabel("موبائل"), 1, 2)
        grid.addWidget(self.btn_find, 1, 3)

        nav = QHBoxLayout()
        nav.setSpacing(2)
        self.btn_first = QPushButton("◀◀")
        self.btn_prev = QPushButton("◀")
        self.btn_next = QPushButton("▶")
        self.btn_last = QPushButton("▶▶")
        self.btn_save = QPushButton("Save")
        for b in (self.btn_first, self.btn_prev, self.btn_next, self.btn_last):
            b.setFixedWidth(28)
            b.setStyleSheet("QPushButton{background:#c33;color:#fff;border:1px solid #777;}")
            nav.addWidget(b)
        self.btn_save.setStyleSheet(
            "QPushButton{background:#bbbbbb;border:1px solid #555;padding:2px 12px;font-weight:bold;}"
        )
        nav.addWidget(self.btn_save)
        self.btn_first.clicked.connect(self._on_first_customer)
        self.btn_prev.clicked.connect(self._on_prev_customer)
        self.btn_next.clicked.connect(self._on_next_customer)
        self.btn_last.clicked.connect(self._on_last_customer)
        self.btn_save.clicked.connect(self._on_save_customer)

        self.field_receipt_no = _InputField()
        self.field_receipt_no.setFixedWidth(80)
        nav.addWidget(self.field_receipt_no)
        nav.addWidget(QLabel("رسید نمبر"))
        grid.addLayout(nav, 2, 0, 1, 4)

        f.setLayout(grid)
        return f

    def _build_naqad_panel(self) -> QFrame:
        f = QFrame()
        f.setStyleSheet("QFrame{background:#ffffff;border:1px solid #aaa;}")
        v = QVBoxLayout()
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(0)

        title = QLabel("نقد")
        title.setStyleSheet(f"background:{HEADER_GRAY};color:#fff;padding:3px;font-weight:bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.addWidget(title)

        self.naqad_table = self._build_tx_table(
            ["سونا وزن", "پوائنٹ", "خالص سونا", "ریٹ", "قیمت"],
            ["خالص سونا نقد فروخت کیا:", "خالص سونا نقد خریدا:"],
        )
        v.addWidget(self.naqad_table)
        f.setLayout(v)
        return f

    def _build_udhaar_panel(self) -> QFrame:
        f = QFrame()
        f.setStyleSheet("QFrame{background:#ffffff;border:1px solid #aaa;}")
        v = QVBoxLayout()
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(0)

        title = QLabel("ادھار")
        title.setStyleSheet(f"background:{HEADER_GRAY};color:#fff;padding:3px;font-weight:bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.addWidget(title)

        self.udhaar_table = self._build_tx_table(
            ["سونا وزن", "پوائنٹ", "خالص سونا", "ریٹ", "قیمت"],
            ["خالص سونا. دیا:", "خالص سونا. لیا:", "کیش دیا:", "کیش لیا:", "ٹوٹل:"],
            yellow_total=True,
        )
        v.addWidget(self.udhaar_table)

        ln = QHBoxLayout()
        ln.setContentsMargins(4, 4, 4, 4)
        ln.setSpacing(6)
        ln.addWidget(QLabel("سونا لین دین:"))
        self.sona_len_den = _ReadField()
        self.sona_len_den.setStyleSheet(
            f"QLineEdit{{background:{FIELD_YELLOW};border:1px solid #888;padding:2px;}}"
        )
        ln.addWidget(self.sona_len_den)
        ln.addWidget(QLabel("کیش لین دین:"))
        self.cash_len_den = _ReadField()
        self.cash_len_den.setStyleSheet(
            f"QLineEdit{{background:{FIELD_YELLOW};border:1px solid #888;padding:2px;}}"
        )
        ln.addWidget(self.cash_len_den)
        v.addLayout(ln)

        f.setLayout(v)
        return f

    def _build_tx_table(
        self,
        headers: list[str],
        row_labels: list[str],
        yellow_total: bool = False,
    ) -> QTableWidget:
        """Reusable 5-column transaction table (Wazan/Point/Khalis/Rate/Qeemat)."""
        table = QTableWidget(len(row_labels), len(headers) + 1)
        table.setHorizontalHeaderLabels([""] + headers)
        table.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        table.verticalHeader().hide()
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setEditTriggers(QTableWidget.EditTrigger.AllEditTriggers)
        table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        table.setStyleSheet(
            "QTableWidget{background:#fff;color:#111;gridline-color:#bbb;}"
            f"QHeaderView::section{{background:{HEADER_GRAY};color:#fff;padding:3px;border:1px solid #777;}}"
            "QTableWidget::item{padding:2px;}"
        )
        for i, label in enumerate(row_labels):
            item = QTableWidgetItem(label)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            table.setItem(i, 0, item)
            for c in range(1, len(headers) + 1):
                cell = QTableWidgetItem("-")
                cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if yellow_total and i == len(row_labels) - 1:
                    cell.setBackground(Qt.GlobalColor.yellow)
                table.setItem(i, c, cell)
        table.itemChanged.connect(self._on_tx_table_changed)
        table.setMinimumHeight(120)
        return table

    def _build_purity_table_frame(self) -> QFrame:
        f = QFrame()
        f.setStyleSheet("QFrame{background:#ffffff;border:1px solid #aaa;}")
        v = QVBoxLayout()
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(0)

        headers = [
            "پرچی",
            "باقی رقم",
            "لیب چارجز",
            "ٹوٹل رقم",
            "سوناریٹ",
            "رتی",
            "ماشہ",
            "تولہ",
            "ملاوٹ فی گرام",
            "خالص سونا (گرام)",
        ]
        metals = list(purity_module.METALS.keys())
        self.purity_table = QTableWidget(len(metals), len(headers) + 1)
        self.purity_table.setHorizontalHeaderLabels([""] + headers)
        self.purity_table.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.purity_table.verticalHeader().hide()
        self.purity_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.purity_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.purity_table.setStyleSheet(
            "QTableWidget{background:#fff;color:#111;gridline-color:#bbb;}"
            f"QHeaderView::section{{background:{HEADER_GRAY};color:#fff;padding:3px;border:1px solid #777;}}"
            "QTableWidget::item{padding:2px;}"
        )
        for i, metal in enumerate(metals):
            metal_item = QTableWidgetItem(metal)
            metal_item.setFlags(metal_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.purity_table.setItem(i, 0, metal_item)
            # Parchi checkbox
            check = QCheckBox()
            check.setStyleSheet("QCheckBox{margin-left:8px;margin-right:8px;}")
            self.purity_table.setCellWidget(i, 1, check)
            for c in range(2, len(headers) + 1):
                cell = QTableWidgetItem("-")
                cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.purity_table.setItem(i, c, cell)
        self.purity_table.setMinimumHeight(200)
        v.addWidget(self.purity_table)
        f.setLayout(v)
        return f

    def _build_receipt_panels_row(self) -> QFrame:
        f = QFrame()
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(6)
        row.addWidget(self._build_left_side_buttons(), 0)
        row.addWidget(self._build_wosooli_receipt(), 1)
        row.addWidget(self._build_lab_receipt(), 1)
        row.addWidget(self._build_udhaar_receipt(), 1)
        row.addWidget(self._build_naqad_receipt(), 1)
        f.setLayout(row)
        return f

    def _build_left_side_buttons(self) -> QFrame:
        f = QFrame()
        f.setStyleSheet("QFrame{background:#ffffff;border:1px solid #aaa;}")
        v = QVBoxLayout()
        v.setContentsMargins(4, 4, 4, 4)
        v.setSpacing(4)
        rows = [
            ("پرچون لیا", "purchun_liya"),
            ("کل اجرت لینی ہے", "kul_ujrat"),
            ("اجرت کا سونا", "ujrat_sona"),
            ("اجرت کی رقم", "ujrat_raqam"),
            ("اجرت وصول کی", "ujrat_wasool"),
            ("ڈسکاؤنٹ", "discount"),
            ("سونا دینا ہے", "sona_dena"),
            ("کیش دیا", "cash_diya"),
            ("سونا دیا", "sona_diya"),
        ]
        self.side_fields: dict[str, _ReadField] = {}
        for label, attr in rows:
            v.addWidget(QLabel(label))
            field = _ReadField()
            field.setStyleSheet(
                f"QLineEdit{{background:{FIELD_GREEN};border:1px solid #888;padding:2px;}}"
            )
            self.side_fields[attr] = field
            v.addWidget(field)
        v.addStretch()
        f.setLayout(v)
        f.setFixedWidth(110)
        return f

    def _build_wosooli_receipt(self) -> QFrame:
        f, body = self._receipt_shell("وصولی رسید")
        self.wosooli_time = QLabel("--:-- --")
        self.wosooli_time.setStyleSheet("background:#bbbbbb;padding:2px 8px;font-weight:bold;")
        body.addWidget(self.wosooli_time, 0, Qt.AlignmentFlag.AlignCenter)

        form = QGridLayout()
        form.setSpacing(4)
        self.wosooli_no = _ReadField()
        self.wosooli_date = _ReadField()
        self.wosooli_time2 = _ReadField()
        self.wosooli_name = _ReadField()
        self.wosooli_rate_per_tola = _ReadField()
        self.wosooli_parchoon = _ReadField()
        self.wosooli_khalis_sona = _ReadField()
        self.wosooli_ujrat_ki_raqam = _ReadField()
        self.wosooli_ujrat_ka_sona = _ReadField()
        self.wosooli_sona_dena = _ReadField()
        self.wosooli_cash_diya = _InputField()
        self.wosooli_cash_diya.setStyleSheet(
            f"QLineEdit{{background:{FIELD_YELLOW};border:1px solid #888;padding:2px;}}"
        )
        self.wosooli_cash_ka_sona = _ReadField()
        self.wosooli_cash_ka_sona.setStyleSheet(
            f"QLineEdit{{background:{FIELD_YELLOW};border:1px solid #888;padding:2px;}}"
        )
        self.wosooli_ujrat_leni = _ReadField()
        self.wosooli_ujrat_leni.setStyleSheet(
            f"QLineEdit{{background:{FIELD_YELLOW};border:1px solid #888;padding:2px;}}"
        )
        self.wosooli_khalis_diya = _ReadField()
        self.wosooli_khalis_diya.setStyleSheet(
            f"QLineEdit{{background:{FIELD_YELLOW};border:1px solid #888;padding:2px;}}"
        )
        self.wosooli_ujrat_wasool = _ReadField()
        self.wosooli_discount = _ReadField()
        self.wosooli_baqi = _ReadField()
        self.wosooli_baqi.setStyleSheet(
            f"QLineEdit{{background:{FIELD_YELLOW};border:1px solid #888;padding:2px;font-weight:bold;}}"
        )

        rows = [
            ("رسید نمبر:", self.wosooli_no, "تاریخ:", self.wosooli_date),
            ("نام:", self.wosooli_name, "وقت:", self.wosooli_time2),
            ("ریٹ فی تولہ:", self.wosooli_rate_per_tola, "پر چون وزن:", self.wosooli_parchoon),
            ("خالص وزن:", self.wosooli_khalis_sona, "اجرت کا سونا:", self.wosooli_ujrat_ka_sona),
            ("اجرت کی رقم:", self.wosooli_ujrat_ki_raqam, "سونا دینا ہے:", self.wosooli_sona_dena),
            ("کیش دیا:", self.wosooli_cash_diya, "کیش کا سونا:", self.wosooli_cash_ka_sona),
            ("اجرت لینی ہے:", self.wosooli_ujrat_leni, "خالص سونا دیا:", self.wosooli_khalis_diya),
            ("اجرت وصول:", self.wosooli_ujrat_wasool, "ڈسکاؤنٹ:", self.wosooli_discount),
            ("باقی:", self.wosooli_baqi, "", QLabel("")),
        ]
        for r, (l1, w1, l2, w2) in enumerate(rows):
            form.addWidget(QLabel(l1), r, 0)
            form.addWidget(w1, r, 1)
            form.addWidget(QLabel(l2), r, 2)
            form.addWidget(w2, r, 3)
        body.addLayout(form)
        self._receipt_action_row(body, prefix="wosooli")
        f.setLayout(body)
        return f

    def _build_lab_receipt(self) -> QFrame:
        f, body = self._receipt_shell("لیب رسید")
        grid = QGridLayout()
        grid.setSpacing(4)
        headers = ["رتی", "ماشہ", "تولہ", "ملی گرام", "گرام"]
        for c, h in enumerate(headers):
            lbl = QLabel(h)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            grid.addWidget(lbl, 0, c + 1)
        self.lab_aamad_wazan = [_ReadField() for _ in range(5)]
        self.lab_milawat_wazan = [_ReadField() for _ in range(5)]
        self.lab_khalis_wazan = [_ReadField() for _ in range(5)]
        for c in range(5):
            self.lab_milawat_wazan[c].setStyleSheet(
                "QLineEdit{background:#fff;border:1px solid #888;color:#aa0000;padding:2px;}"
            )
            self.lab_khalis_wazan[c].setStyleSheet(
                "QLineEdit{background:#fff;border:1px solid #888;color:#aa0000;padding:2px;}"
            )
        grid.addWidget(QLabel("آمد وزن"), 1, 0)
        grid.addWidget(QLabel("ملاوٹ وزن"), 2, 0)
        grid.addWidget(QLabel("خالص وزن"), 3, 0)
        for c in range(5):
            grid.addWidget(self.lab_aamad_wazan[c], 1, c + 1)
            grid.addWidget(self.lab_milawat_wazan[c], 2, c + 1)
            grid.addWidget(self.lab_khalis_wazan[c], 3, c + 1)
        body.addLayout(grid)

        info = QGridLayout()
        info.setSpacing(4)
        info.addWidget(QLabel("ملاوٹ فی تولہ:"), 0, 0)
        self.lab_milawat_per_tola = _ReadField()
        self.lab_milawat_per_tola.setStyleSheet(
            "QLineEdit{background:#fff;border:1px solid #888;color:#aa0000;padding:2px;font-weight:bold;}"
        )
        info.addWidget(self.lab_milawat_per_tola, 0, 1)
        info.addWidget(QLabel("فی گرام:"), 0, 2)
        self.lab_milawat_per_gram = _ReadField()
        info.addWidget(self.lab_milawat_per_gram, 0, 3)

        info.addWidget(QLabel("کیریٹ:"), 1, 0)
        self.lab_carat = _ReadField()
        info.addWidget(self.lab_carat, 1, 1)
        info.addWidget(QLabel("ریٹ فی تولہ:"), 1, 2)
        self.lab_rate_per_tola = _ReadField()
        info.addWidget(self.lab_rate_per_tola, 1, 3)

        info.addWidget(QLabel("ٹوٹل رقم:"), 2, 0)
        self.lab_total_raqam = _ReadField()
        self.lab_total_raqam.setStyleSheet(
            f"QLineEdit{{background:{FIELD_YELLOW};border:1px solid #888;padding:2px;font-weight:bold;}}"
        )
        info.addWidget(self.lab_total_raqam, 2, 1)
        info.addWidget(QLabel("چارجز:"), 2, 2)
        self.lab_charges = _ReadField()
        info.addWidget(self.lab_charges, 2, 3)

        info.addWidget(QLabel("بقایا رقم:"), 3, 0)
        self.lab_baqaya = _ReadField()
        info.addWidget(self.lab_baqaya, 3, 1)
        info.addWidget(QLabel("نام:"), 3, 2)
        self.lab_name = _ReadField()
        info.addWidget(self.lab_name, 3, 3)

        info.addWidget(QLabel("پوائنٹ:"), 4, 0)
        self.lab_point = _ReadField()
        info.addWidget(self.lab_point, 4, 1)
        info.addWidget(QLabel("تاریخ:"), 4, 2)
        self.lab_date = _ReadField()
        info.addWidget(self.lab_date, 4, 3)

        info.addWidget(QLabel("رتی:"), 5, 0)
        self.lab_rati = _ReadField()
        info.addWidget(self.lab_rati, 5, 1)
        info.addWidget(QLabel("وقت:"), 5, 2)
        self.lab_time = _ReadField()
        info.addWidget(self.lab_time, 5, 3)
        body.addLayout(info)

        saved_row = QHBoxLayout()
        self.lab_saved_chk = QCheckBox("Saved")
        saved_row.addWidget(self.lab_saved_chk)
        saved_row.addStretch()
        body.addLayout(saved_row)
        self._receipt_action_row(body, prefix="lab", with_receipt_btn=True)
        f.setLayout(body)
        return f

    def _build_udhaar_receipt(self) -> QFrame:
        f, body = self._receipt_shell("ادھار کی رسید")
        form = QGridLayout()
        form.setSpacing(4)
        self.udhaar_r_no = _ReadField()
        self.udhaar_r_date = _ReadField()
        self.udhaar_r_name = _ReadField()
        self.udhaar_r_rate_gram = _ReadField()
        self.udhaar_r_rate_tola = _ReadField()
        self.udhaar_r_sona_diya = _ReadField()
        self.udhaar_r_sona_liya = _ReadField()
        self.udhaar_r_baqi = _ReadField()
        self.udhaar_r_sabqa_sona_balance = _ReadField()
        self.udhaar_r_sabqa_sona_balance.setStyleSheet(
            f"QLineEdit{{background:{FIELD_YELLOW};border:1px solid #888;padding:2px;}}"
        )
        self.udhaar_r_cash_diya = _ReadField()
        self.udhaar_r_cash_liya = _ReadField()
        self.udhaar_r_cash_baqi = _ReadField()
        self.udhaar_r_sabqa_cash_balance = _ReadField()
        self.udhaar_r_sabqa_cash_balance.setStyleSheet(
            f"QLineEdit{{background:{FIELD_YELLOW};border:1px solid #888;padding:2px;}}"
        )

        rows = [
            ("رسید نمبر:", self.udhaar_r_no, "تاریخ:", self.udhaar_r_date),
            ("نام:", self.udhaar_r_name, "", QLabel("")),
            ("ریٹ فی تولہ:", self.udhaar_r_rate_tola, "ریٹ فی گرام:", self.udhaar_r_rate_gram),
            ("سونا. دیا:", self.udhaar_r_sona_diya, "", QLabel("")),
            ("سونا. لیا:", self.udhaar_r_sona_liya, "", QLabel("")),
            ("باقی:", self.udhaar_r_baqi, "سابقہ سونا بیلنس:", self.udhaar_r_sabqa_sona_balance),
            ("کیش. دیا:", self.udhaar_r_cash_diya, "", QLabel("")),
            ("کیش. لیا:", self.udhaar_r_cash_liya, "", QLabel("")),
            ("باقی:", self.udhaar_r_cash_baqi, "سابقہ کیش بیلنس:", self.udhaar_r_sabqa_cash_balance),
        ]
        for r, (l1, w1, l2, w2) in enumerate(rows):
            form.addWidget(QLabel(l1), r, 0)
            form.addWidget(w1, r, 1)
            form.addWidget(QLabel(l2), r, 2)
            form.addWidget(w2, r, 3)
        body.addLayout(form)
        self._receipt_action_row(body, prefix="udhaar_r", with_refresh=True)
        f.setLayout(body)
        return f

    def _build_naqad_receipt(self) -> QFrame:
        f, body = self._receipt_shell("نقدی کی رسید")
        title2 = QLabel("رسید سونا خرید")
        title2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title2.setStyleSheet("font-weight:bold;padding:2px;")
        body.addWidget(title2)

        form = QGridLayout()
        form.setSpacing(4)
        self.naqad_r_no = _ReadField()
        self.naqad_r_date = _ReadField()
        self.naqad_r_name = _ReadField()
        self.naqad_r_rate_gram = _ReadField()
        self.naqad_r_rate_tola = _ReadField()
        self.naqad_r_tola = _ReadField()
        self.naqad_r_masha = _ReadField()
        self.naqad_r_rati = _ReadField()
        self.naqad_r_point = _InputField()
        self.naqad_r_sona_wazan = _ReadField()
        self.naqad_r_khalis_wazan = _ReadField()
        self.naqad_r_kul_qeemat = _ReadField()
        self.naqad_r_raqam_di = _ReadField()
        self.naqad_r_balance = _ReadField()
        self.naqad_r_balance.setStyleSheet(
            f"QLineEdit{{background:{FIELD_YELLOW};border:1px solid #888;padding:2px;font-weight:bold;}}"
        )

        rows = [
            ("رسید نمبر:", self.naqad_r_no, "تاریخ:", self.naqad_r_date),
            ("نام:", self.naqad_r_name, "", QLabel("")),
            ("ریٹ فی تولہ:", self.naqad_r_rate_tola, "ریٹ فی گرام:", self.naqad_r_rate_gram),
        ]
        for r, (l1, w1, l2, w2) in enumerate(rows):
            form.addWidget(QLabel(l1), r, 0)
            form.addWidget(w1, r, 1)
            form.addWidget(QLabel(l2), r, 2)
            form.addWidget(w2, r, 3)
        body.addLayout(form)

        tmr = QHBoxLayout()
        tmr.addWidget(QLabel("تولہ"))
        tmr.addWidget(self.naqad_r_tola)
        tmr.addWidget(QLabel("ماشہ"))
        tmr.addWidget(self.naqad_r_masha)
        tmr.addWidget(QLabel("رتی"))
        tmr.addWidget(self.naqad_r_rati)
        body.addLayout(tmr)

        pf = QGridLayout()
        pf.setSpacing(4)
        pf.addWidget(QLabel("پوائنٹ"), 0, 0)
        pf.addWidget(self.naqad_r_point, 0, 1)
        pf.addWidget(QLabel("سونا وزن:"), 1, 0)
        pf.addWidget(self.naqad_r_sona_wazan, 1, 1)
        pf.addWidget(QLabel("خالص وزن:"), 2, 0)
        pf.addWidget(self.naqad_r_khalis_wazan, 2, 1)
        pf.addWidget(QLabel("کل قیمت:"), 3, 0)
        pf.addWidget(self.naqad_r_kul_qeemat, 3, 1)
        pf.addWidget(QLabel("رقم دی:"), 4, 0)
        pf.addWidget(self.naqad_r_raqam_di, 4, 1)
        pf.addWidget(QLabel("بیلنس:"), 5, 0)
        pf.addWidget(self.naqad_r_balance, 5, 1)
        body.addLayout(pf)

        self._receipt_action_row(body, prefix="naqad_r", with_view=True)
        f.setLayout(body)
        return f

    def _receipt_shell(self, title: str) -> tuple[QFrame, QVBoxLayout]:
        f = QFrame()
        f.setStyleSheet("QFrame{background:#ffffff;border:1px solid #aaa;}")
        v = QVBoxLayout()
        v.setContentsMargins(4, 4, 4, 4)
        v.setSpacing(4)
        bar = QLabel(title)
        bar.setStyleSheet(f"background:{HEADER_GRAY};color:#fff;padding:3px;font-weight:bold;")
        bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.addWidget(bar)
        return f, v

    def _receipt_action_row(
        self,
        body: QVBoxLayout,
        prefix: str,
        with_receipt_btn: bool = False,
        with_refresh: bool = False,
        with_view: bool = False,
    ) -> None:
        row = QHBoxLayout()
        for code in ("I", "C", "R", "P", "O"):
            b = QPushButton(code)
            b.setFixedWidth(28)
            b.setStyleSheet("QPushButton{background:#ddd;border:1px solid #888;}")
            row.addWidget(b)
        wa = QPushButton("WhatsApp")
        wa.setStyleSheet(
            "QPushButton{color:#0d8a3a;background:transparent;border:none;font-weight:bold;}"
        )
        wa.clicked.connect(lambda _, p=prefix: self._on_whatsapp(p))
        row.addWidget(wa)
        printer = QPushButton("🖨")
        printer.setFixedWidth(28)
        printer.clicked.connect(lambda _, p=prefix: self._on_print(p))
        row.addWidget(printer)
        if with_receipt_btn:
            rec = QPushButton("رسید")
            rec.clicked.connect(lambda _, p=prefix: self._on_save_receipt(p))
            row.addWidget(rec)
        if with_refresh:
            rf = QPushButton("Refresh")
            rf.clicked.connect(self._refresh_totals)
            row.addWidget(rf)
        if with_view:
            view = QPushButton("View")
            x = QPushButton("X")
            x.setStyleSheet("QPushButton{background:#c33;color:#fff;border:1px solid #777;}")
            add = QPushButton("Add")
            add.clicked.connect(lambda _, p=prefix: self._on_save_receipt(p))
            row.addWidget(view)
            row.addWidget(x)
            row.addWidget(add)
        row.addStretch()
        body.addLayout(row)

    def _build_footer_totals(self) -> QFrame:
        f = QFrame()
        f.setStyleSheet("QFrame{background:#dddddd;border:1px solid #888;}")
        row = QHBoxLayout()
        row.setContentsMargins(6, 4, 6, 4)
        row.setSpacing(10)
        self.btn_defaults = QPushButton("Defaults")
        self.btn_defaults.setStyleSheet("QPushButton{background:#cccccc;border:1px solid #777;padding:3px 14px;}")
        self.btn_defaults.clicked.connect(self._on_defaults)
        row.addWidget(self.btn_defaults)

        def green_label(text: str) -> tuple[QLabel, QLineEdit]:
            l = QLabel(text)
            v = QLineEdit("-")
            v.setReadOnly(True)
            v.setAlignment(Qt.AlignmentFlag.AlignCenter)
            v.setFixedWidth(140)
            v.setStyleSheet("QLineEdit{background:#1f6f3e;color:#fff;font-weight:bold;border:1px solid #444;padding:3px;}")
            return l, v

        l1, self.total_cash = green_label("دکان میں موجود کیش:")
        l2, self.total_tezabi = green_label("دکان میں موجود تیزابی سونا:")
        l3, self.total_purchun = green_label("دکان میں موجود پرچون:")
        for l, w in [(l1, self.total_cash), (l2, self.total_tezabi), (l3, self.total_purchun)]:
            row.addWidget(l)
            row.addWidget(w)
        row.addStretch()
        f.setLayout(row)
        return f

    # ─────────────────────────────────────────────────────────────────
    # Signal wiring + formulas
    # ─────────────────────────────────────────────────────────────────
    def _wire_rate_signals(self) -> None:
        self.rate_per_tola.textChanged.connect(self._on_rate_changed)
        self.parchi_charge.textChanged.connect(self._recompute_purity_rows)
        self.per_gram_charge.textChanged.connect(self._recompute_purity_rows)

    def _wire_weight_signals(self) -> None:
        self.air_grams.textChanged.connect(self._on_weight_changed)
        self.water_grams.textChanged.connect(self._on_weight_changed)
        self.naqad_r_point.textChanged.connect(self._recompute_naqad_receipt)

    def _to_float(self, text: str) -> float:
        try:
            return float(text.replace(",", "").strip())
        except (ValueError, AttributeError):
            return 0.0

    def _on_rate_changed(self) -> None:
        rate_tola = self._to_float(self.rate_per_tola.text())
        rate_gram = units.rate_per_gram_from_tola(rate_tola)
        self.rate_per_gram.setText(f"{rate_gram:.4f}" if rate_gram else "-")
        # propagate
        self.lab_rate_per_tola.setText(_num(rate_tola, 2))
        self.lab_milawat_per_gram.setText(_num(rate_gram, 4))
        self.naqad_r_rate_tola.setText(_num(rate_tola, 2))
        self.naqad_r_rate_gram.setText(_num(rate_gram, 4))
        self.udhaar_r_rate_tola.setText(_num(rate_tola, 2))
        self.udhaar_r_rate_gram.setText(_num(rate_gram, 4))
        self.wosooli_rate_per_tola.setText(_num(rate_tola, 2))
        self._recompute_purity_rows()
        self._recompute_naqad_receipt()

    def _on_weight_changed(self) -> None:
        air = self._to_float(self.air_grams.text())
        water = self._to_float(self.water_grams.text())
        # update breakdowns
        for grams, fields in (
            (air, (self.air_tola, self.air_masha, self.air_rati)),
            (water, (self.water_tola, self.water_masha, self.water_rati)),
        ):
            bd = units.decompose(units.grams_to_tola(grams))
            fields[0].setText(str(bd.tola) if bd.tola else "-")
            fields[1].setText(str(bd.masha) if bd.masha else "-")
            fields[2].setText(f"{bd.rati:.2f}" if bd.rati else "-")
        self._recompute_purity_rows()

    def _recompute_purity_rows(self) -> None:
        air = self._to_float(self.air_grams.text())
        water = self._to_float(self.water_grams.text())
        if not air or not water or water >= air:
            return
        try:
            rows = purity_module.calculate_all(air, water)
        except ValueError:
            return
        rate_tola = self._to_float(self.rate_per_tola.text())
        parchi_charge = self._to_float(self.parchi_charge.text())
        per_gram_charge = self._to_float(self.per_gram_charge.text())

        for i, (metal, row) in enumerate(rows.items()):
            khalis_g = row.pure_gold_grams
            milawat_g_per_g = round(1 - row.purity_percent / 100, 4)
            khalis_tola = units.grams_to_tola(khalis_g)
            bd = units.decompose(khalis_tola)
            total = units.price_from_grams(khalis_g, rate_tola)
            lab_charge = per_gram_charge * air + parchi_charge if air else 0.0
            baqi = max(total - lab_charge, 0.0)
            cells = [
                (2, _num(khalis_g, 4)),  # خالص سونا (گرام)
                (3, _num(milawat_g_per_g, 4)),  # ملاوٹ فی گرام
                (4, str(bd.tola) if bd.tola else "-"),
                (5, str(bd.masha) if bd.masha else "-"),
                (6, f"{bd.rati:.2f}" if bd.rati else "-"),
                (7, "-"),  # سوناریٹ (per-row, left for future)
                (8, _money(rate_tola)),
                (9, _money(lab_charge)),
                (10, _money(baqi)),
            ]
            for col, text in cells:
                item = self.purity_table.item(i, col)
                if item:
                    item.setText(text)

    def _recompute_naqad_receipt(self) -> None:
        rate_tola = self._to_float(self.rate_per_tola.text())
        sona_wazan = self._to_float(self.naqad_r_sona_wazan.text())
        point = self._to_float(self.naqad_r_point.text())
        khalis = sona_wazan  # cash receipt assumes full purity unless purity row applied
        self.naqad_r_khalis_wazan.setText(_num(khalis, 4))
        price = units.price_from_grams(khalis, rate_tola)
        # add fractional point as fraction-of-tola
        price += point / units.POINT_PER_TOLA * rate_tola if rate_tola else 0
        self.naqad_r_kul_qeemat.setText(_money(price))
        raqam_di = self._to_float(self.naqad_r_raqam_di.text())
        self.naqad_r_balance.setText(_money(price - raqam_di))

    def _on_tx_table_changed(self, item: QTableWidgetItem) -> None:
        # update sona/cash totals from naqad + udhaar tables
        self._refresh_totals()

    # ─────────────────────────────────────────────────────────────────
    # Clock
    # ─────────────────────────────────────────────────────────────────
    def _init_clock(self) -> None:
        self.clock = QTimer(self)
        self.clock.timeout.connect(self._tick)
        self.clock.start(1000)
        self._tick()

    def _tick(self) -> None:
        if self._clock_frozen:
            return
        now = datetime.now()
        date_str = now.strftime("%d-%m-%y")
        time_str = now.strftime("%I:%M %p")
        self.wosooli_time.setText(time_str)
        self.wosooli_date.setText(date_str)
        self.wosooli_time2.setText(time_str)
        self.lab_date.setText(date_str)
        self.lab_time.setText(time_str)
        self.udhaar_r_date.setText(date_str)
        self.naqad_r_date.setText(date_str)

    # ─────────────────────────────────────────────────────────────────
    # Customer handlers
    # ─────────────────────────────────────────────────────────────────
    def _set_receipt_no(self, n: int) -> None:
        self.field_receipt_no.setText(str(n))
        self.wosooli_no.setText(str(n))
        self.udhaar_r_no.setText(str(n))
        self.naqad_r_no.setText(str(n))

    def _current_form_data(self) -> dict:
        return {
            "name": self.field_name.currentText().strip(),
            "mobile": self.field_mobile.currentText().strip(),
            "receipt_no": self._to_float(self.field_receipt_no.text()),
        }

    def _on_new_customer(self) -> None:
        self._on_clear_form()
        self._set_receipt_no(self.customer_svc.next_receipt_no())

    def _on_clear_form(self) -> None:
        self._current_customer_id = None
        self.field_name.setCurrentText("")
        self.field_mobile.setCurrentText("")
        for f in (self.naqad_r_name, self.udhaar_r_name, self.lab_name, self.wosooli_name):
            f.setText("-")

    def _on_find_customer(self) -> None:
        query = self.field_name.currentText().strip() or self.field_mobile.currentText().strip()
        if not query:
            QMessageBox.warning(self, "خرابی", "براہ کرم تلاش کے لیے نام یا موبائل درج کریں")
            return
        results = self.customer_svc.search(query)
        if not results:
            QMessageBox.information(self, "تلاش", "کوئی کسٹمر نہیں ملا")
            return
        self._customer_cache = results
        self._customer_index = 0
        self._load_customer(results[0])

    def _load_customer(self, row) -> None:
        self._current_customer_id = row["id"]
        self.field_name.setCurrentText(row["name"])
        self.field_mobile.setCurrentText(row["mobile"] or "")
        for f in (self.naqad_r_name, self.udhaar_r_name, self.lab_name, self.wosooli_name):
            f.setText(row["name"])

    def _on_save_customer(self) -> None:
        data = self._current_form_data()
        if not data["name"]:
            QMessageBox.warning(self, "خرابی", "کسٹمر کا نام درج کریں")
            return
        try:
            if self._current_customer_id:
                self.customer_svc.update(self._current_customer_id, data["name"], data["mobile"])
                msg = "کسٹمر اپ ڈیٹ ہو گیا"
            else:
                new_id = self.customer_svc.add(data["name"], data["mobile"])
                self._current_customer_id = new_id
                msg = "کسٹمر شامل ہو گیا"
            QMessageBox.information(self, "محفوظ", msg)
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(self, "خرابی", str(exc))

    def _on_first_customer(self) -> None:
        all_c = self.customer_svc.list_all()
        if not all_c:
            return
        self._customer_cache = all_c
        self._customer_index = 0
        self._load_customer(all_c[0])

    def _on_last_customer(self) -> None:
        all_c = self.customer_svc.list_all()
        if not all_c:
            return
        self._customer_cache = all_c
        self._customer_index = len(all_c) - 1
        self._load_customer(all_c[-1])

    def _on_prev_customer(self) -> None:
        if not self._customer_cache:
            self._customer_cache = self.customer_svc.list_all()
            self._customer_index = len(self._customer_cache)
        if self._customer_index > 0:
            self._customer_index -= 1
            self._load_customer(self._customer_cache[self._customer_index])

    def _on_next_customer(self) -> None:
        if not self._customer_cache:
            self._customer_cache = self.customer_svc.list_all()
            self._customer_index = -1
        if self._customer_index + 1 < len(self._customer_cache):
            self._customer_index += 1
            self._load_customer(self._customer_cache[self._customer_index])

    # ─────────────────────────────────────────────────────────────────
    # Save / WhatsApp / print
    # ─────────────────────────────────────────────────────────────────
    def _on_save_receipt(self, prefix: str) -> None:
        try:
            payload = self._collect_receipt_payload(prefix)
            self.customer_svc.save_receipt(payload)
            QMessageBox.information(self, "محفوظ", "رسید محفوظ ہو گئی")
            self._refresh_totals()
            self._set_receipt_no(self.customer_svc.next_receipt_no())
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(self, "خرابی", str(exc))

    def _collect_receipt_payload(self, prefix: str) -> dict:
        type_map = {
            "wosooli": "wosooli",
            "lab": "lab",
            "udhaar_r": "udhaar",
            "naqad_r": "cash",
        }
        rate_tola = self._to_float(self.rate_per_tola.text())
        rate_gram = self._to_float(self.rate_per_gram.text())
        receipt_no = int(self._to_float(self.field_receipt_no.text()))
        total = self._to_float(self.naqad_r_kul_qeemat.text())
        paid = self._to_float(self.naqad_r_raqam_di.text())
        return {
            "receipt_no": receipt_no,
            "customer_id": self._current_customer_id,
            "receipt_type": type_map[prefix],
            "receipt_date": datetime.now().isoformat(),
            "gold_weight": self._to_float(self.naqad_r_sona_wazan.text()),
            "point": self._to_float(self.naqad_r_point.text()),
            "khalis_sona": self._to_float(self.naqad_r_khalis_wazan.text()),
            "rate_per_tola": rate_tola,
            "rate_per_gram": rate_gram,
            "total_amount": total,
            "paid_amount": paid,
            "balance": total - paid,
            "labor_charge": self._to_float(self.lab_charges.text()),
            "notes": "",
        }

    def _on_whatsapp(self, prefix: str) -> None:
        QMessageBox.information(self, "WhatsApp", f"WhatsApp share placeholder ({prefix})")

    def _on_print(self, prefix: str) -> None:
        try:
            rows = [{"name": self.field_name.currentText() or "-", "qty": 1, "amount": _money(self._to_float(self.naqad_r_kul_qeemat.text()))}]
            path = self.report_svc.generate_invoice(rows, self._to_float(self.naqad_r_kul_qeemat.text()))
            QMessageBox.information(self, "پرنٹ", f"پرنٹ فائل تیار: {path}")
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(self, "خرابی", str(exc))

    # ─────────────────────────────────────────────────────────────────
    # Footer totals
    # ─────────────────────────────────────────────────────────────────
    def _refresh_totals(self) -> None:
        try:
            totals = self.customer_svc.totals_by_type()
        except Exception:
            return
        cash_total = totals.get("cash", {}).get("total", 0)
        udhaar_balance = totals.get("udhaar", {}).get("balance", 0)
        khalis_total = sum(t.get("khalis", 0) for t in totals.values())
        self.total_cash.setText(_money(cash_total))
        self.total_tezabi.setText(_money(khalis_total))
        self.total_purchun.setText(_money(udhaar_balance))

    def _on_defaults(self) -> None:
        self.rate_per_tola.setText("9000")
        self.parchi_charge.setText("100")
        self.per_gram_charge.setText("80")

    # ─────────────────────────────────────────────────────────────────
    # Tab actions
    # ─────────────────────────────────────────────────────────────────
    def _open_roznamcha(self) -> None:
        RoznamchaDialog(self).show()

    def _open_lab_dialog(self) -> None:
        LabDialog(self).show()

    def _open_udhaar_dialog(self) -> None:
        UdhaarDialog(self).show()


# ─────────────────────────────────────────────────────────────────
# Dialogs (placeholder + customer record)
# ─────────────────────────────────────────────────────────────────
class _DialogShell(QMainWindow):
    def __init__(self, parent, title: str) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setMinimumSize(700, 400)


class RoznamchaDialog(_DialogShell):
    def __init__(self, parent) -> None:
        super().__init__(parent, "روزنامچہ")
        c = QWidget()
        v = QVBoxLayout()
        v.addWidget(QLabel("روزنامچہ — اس صفحے پر تمام لین دین ظاہر کیے جائیں گے"))
        c.setLayout(v)
        self.setCentralWidget(c)


class LabDialog(_DialogShell):
    def __init__(self, parent) -> None:
        super().__init__(parent, "لیب")
        c = QWidget()
        v = QVBoxLayout()
        v.addWidget(QLabel("لیب — یہاں لیب رسیدیں اور پرچی ریکارڈ ہوں گی"))
        c.setLayout(v)
        self.setCentralWidget(c)


class UdhaarDialog(_DialogShell):
    """Customer record + ادھار لین دین action panel from screenshot #9."""

    def __init__(self, parent) -> None:
        super().__init__(parent, "ادھار / کسٹمر ریکارڈ")
        c = QWidget()
        outer = QHBoxLayout()

        # left: customer record
        left = QFrame()
        left.setStyleSheet("QFrame{background:#fff;border:1px solid #888;}")
        lv = QVBoxLayout()
        lv.addWidget(QLabel("کسٹمر ریکارڈ"))
        dr = QHBoxLayout()
        dr.addWidget(QLabel("From Date:"))
        self.from_date = _InputField()
        self.from_date.setText(datetime.now().strftime("%d/%m/%Y"))
        dr.addWidget(self.from_date)
        dr.addWidget(QLabel("To Date:"))
        self.to_date = _InputField()
        self.to_date.setText(datetime.now().strftime("%d/%m/%Y"))
        dr.addWidget(self.to_date)
        lv.addLayout(dr)
        lv.addWidget(QLabel("کسٹمر کا کوڈ:"))
        self.cust_code = QComboBox()
        lv.addWidget(self.cust_code)
        lv.addWidget(QLabel("کسٹمر کا نام:"))
        self.cust_name = QComboBox()
        lv.addWidget(self.cust_name)
        for txt in ("کسٹمر کی تفصیلی رسید", "لیب پر چون جو خریدا ہے", "لیب کی صرف پرچی بنائی ہے"):
            b = QPushButton(txt)
            b.setStyleSheet("QPushButton{background:#cccccc;border:1px solid #777;padding:6px;}")
            lv.addWidget(b)
        lv.addStretch()
        left.setLayout(lv)

        # right: action buttons
        right = QFrame()
        right.setStyleSheet("QFrame{background:#fff;border:1px solid #888;}")
        rv = QVBoxLayout()
        rv.addWidget(QLabel("ادھار لین دین"))
        actions = [
            ("ادھار لینا ہے", "ادھار دینا ہے"),
            ("سونا اور کیش ادھار لیا", "سونا اور کیش ادھار دیا"),
            ("نقد سونا فروخت", "نقد سونا خرید"),
            ("لیب تفصیل", "تحلیل تفصیل"),
        ]
        for a, b in actions:
            h = QHBoxLayout()
            for txt in (a, b):
                btn = QPushButton(txt)
                btn.setStyleSheet("QPushButton{background:#cccccc;border:1px solid #777;padding:8px;}")
                h.addWidget(btn)
            rv.addLayout(h)
        rv.addStretch()
        right.setLayout(rv)

        outer.addWidget(left, 1)
        outer.addWidget(right, 1)
        c.setLayout(outer)
        self.setCentralWidget(c)
