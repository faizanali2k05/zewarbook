from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from config.settings import REPORT_DIR


class ReportService:
    def _canvas(self, prefix: str):
        file_path = REPORT_DIR / f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        return canvas.Canvas(str(file_path), pagesize=A4), file_path

    def generate_invoice(self, rows: list[dict], total: float) -> str:
        c, path = self._canvas("invoice")
        c.drawString(100, 800, "اردو انوائس")
        y = 760
        for row in rows:
            c.drawString(100, y, f"{row['name']} x{row['qty']} = {row['amount']}")
            y -= 20
        c.drawString(100, y - 20, f"Total: {total}")
        c.save()
        return str(path)

    def generate_stock_summary(self, rows: list[dict]) -> str:
        c, path = self._canvas("stock_summary")
        c.drawString(100, 800, "اسٹاک خلاصہ")
        y = 760
        for row in rows:
            c.drawString(100, y, f"{row['name_urdu']} | Qty: {row['quantity']}")
            y -= 20
        c.save()
        return str(path)
