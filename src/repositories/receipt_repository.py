from src.repositories.db import get_connection


class ReceiptRepository:
    def save(self, payload: dict) -> int:
        with get_connection() as conn:
            existing = conn.execute(
                "SELECT id FROM receipts WHERE receipt_no = ?",
                (payload["receipt_no"],),
            ).fetchone()
            if existing:
                conn.execute(
                    """
                    UPDATE receipts SET
                        customer_id = :customer_id,
                        receipt_type = :receipt_type,
                        receipt_date = :receipt_date,
                        gold_weight = :gold_weight,
                        point = :point,
                        khalis_sona = :khalis_sona,
                        rate_per_tola = :rate_per_tola,
                        rate_per_gram = :rate_per_gram,
                        total_amount = :total_amount,
                        paid_amount = :paid_amount,
                        balance = :balance,
                        labor_charge = :labor_charge,
                        notes = :notes
                    WHERE receipt_no = :receipt_no
                    """,
                    payload,
                )
                return existing["id"]
            cur = conn.execute(
                """
                INSERT INTO receipts (
                    receipt_no, customer_id, receipt_type, receipt_date,
                    gold_weight, point, khalis_sona, rate_per_tola, rate_per_gram,
                    total_amount, paid_amount, balance, labor_charge, notes
                ) VALUES (
                    :receipt_no, :customer_id, :receipt_type, :receipt_date,
                    :gold_weight, :point, :khalis_sona, :rate_per_tola, :rate_per_gram,
                    :total_amount, :paid_amount, :balance, :labor_charge, :notes
                )
                """,
                payload,
            )
            return cur.lastrowid

    def get_by_receipt_no(self, receipt_no: int):
        with get_connection() as conn:
            return conn.execute(
                "SELECT * FROM receipts WHERE receipt_no = ?", (receipt_no,)
            ).fetchone()

    def next_receipt_no(self) -> int:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT COALESCE(MAX(receipt_no), 0) + 1 AS n FROM receipts"
            ).fetchone()
            return int(row["n"])

    def list_all(self):
        with get_connection() as conn:
            return conn.execute(
                "SELECT * FROM receipts ORDER BY receipt_no DESC"
            ).fetchall()

    def totals_by_type(self) -> dict:
        with get_connection() as conn:
            rows = conn.execute(
                """
                SELECT receipt_type,
                       COALESCE(SUM(total_amount), 0) AS total,
                       COALESCE(SUM(balance), 0) AS balance,
                       COALESCE(SUM(khalis_sona), 0) AS khalis
                FROM receipts
                GROUP BY receipt_type
                """
            ).fetchall()
            return {r["receipt_type"]: dict(r) for r in rows}
