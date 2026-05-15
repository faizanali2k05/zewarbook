from src.repositories.db import get_connection


class TransactionRepository:
    def create_purchase(self, supplier_id: int, rows: list[dict], notes: str = "") -> int:
        with get_connection() as conn:
            total = sum(r["quantity"] * r["unit_price"] for r in rows)
            cur = conn.execute(
                "INSERT INTO purchases(supplier_id, total_amount, notes) VALUES (?, ?, ?)",
                (supplier_id, total, notes),
            )
            purchase_id = cur.lastrowid
            for row in rows:
                conn.execute(
                    "INSERT INTO purchase_items(purchase_id, item_id, quantity, unit_price) VALUES (?, ?, ?, ?)",
                    (purchase_id, row["item_id"], row["quantity"], row["unit_price"]),
                )
                conn.execute(
                    """
                    INSERT INTO stock_movements(item_id, action, qty_in, qty_out, ref_type, ref_id)
                    VALUES (?, 'purchase', ?, 0, 'purchase', ?)
                    """,
                    (row["item_id"], row["quantity"], purchase_id),
                )
                conn.execute("UPDATE items SET quantity = quantity + ? WHERE id = ?", (row["quantity"], row["item_id"]))
            return purchase_id

    def create_sale(self, customer_id: int, rows: list[dict], notes: str = "") -> int:
        with get_connection() as conn:
            total = sum(r["quantity"] * r["unit_price"] for r in rows)
            cur = conn.execute(
                "INSERT INTO sales(customer_id, total_amount, notes) VALUES (?, ?, ?)",
                (customer_id, total, notes),
            )
            sale_id = cur.lastrowid
            for row in rows:
                conn.execute(
                    "INSERT INTO sale_items(sale_id, item_id, quantity, unit_price) VALUES (?, ?, ?, ?)",
                    (sale_id, row["item_id"], row["quantity"], row["unit_price"]),
                )
                conn.execute(
                    """
                    INSERT INTO stock_movements(item_id, action, qty_in, qty_out, ref_type, ref_id)
                    VALUES (?, 'sale', 0, ?, 'sale', ?)
                    """,
                    (row["item_id"], row["quantity"], sale_id),
                )
                conn.execute("UPDATE items SET quantity = quantity - ? WHERE id = ?", (row["quantity"], row["item_id"]))
            return sale_id

    def get_latest_transaction_note(self) -> str:
        with get_connection() as conn:
            row = conn.execute(
                """
                SELECT notes
                FROM (
                    SELECT notes, created_at FROM sales
                    UNION ALL
                    SELECT notes, created_at FROM purchases
                )
                WHERE notes IS NOT NULL AND TRIM(notes) != ''
                ORDER BY created_at DESC
                LIMIT 1
                """
            ).fetchone()
            return row["notes"] if row else ""

    def save_daily_rates(self, tola: float, gram: float, tezabi: float) -> None:
        """Save daily gold rates to database"""
        with get_connection() as conn:
            # Check if today's rates exist
            today = conn.execute("SELECT DATE('now') as today").fetchone()["today"]
            existing = conn.execute(
                "SELECT id FROM daily_rates WHERE date = ?", (today,)
            ).fetchone()
            
            if existing:
                # Update existing rates
                conn.execute(
                    "UPDATE daily_rates SET rate_tola = ?, rate_gram = ?, rate_tezabi = ? WHERE date = ?",
                    (tola, gram, tezabi, today)
                )
            else:
                # Insert new rates
                conn.execute(
                    "INSERT INTO daily_rates(date, rate_tola, rate_gram, rate_tezabi) VALUES (?, ?, ?, ?)",
                    (today, tola, gram, tezabi)
                )

    def save_transaction(self, receipt_data: dict) -> int:
        """Save transaction receipt to database"""
        with get_connection() as conn:
            # Insert main transaction
            cur = conn.execute(
                """
                INSERT INTO transactions(
                    receipt_number, date, party_name, description, weight, 
                    rate_per_gram, labor_charge, total_amount, paid_amount, balance, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    receipt_data["receipt_number"],
                    receipt_data["date"],
                    receipt_data["party_name"],
                    receipt_data["description"],
                    receipt_data.get("weight", 0),
                    receipt_data.get("rate_per_gram", 0),
                    receipt_data.get("labor_charge", 0),
                    receipt_data.get("total_amount", 0),
                    receipt_data.get("paid_amount", 0),
                    receipt_data.get("balance", 0),
                    receipt_data.get("notes", "")
                )
            )
            transaction_id = cur.lastrowid
            return transaction_id

    def get_next_receipt_number(self) -> int:
        """Get the next available receipt number"""
        with get_connection() as conn:
            row = conn.execute(
                "SELECT MAX(receipt_number) as max_num FROM transactions"
            ).fetchone()
            return (row["max_num"] or 0) + 1

    def get_transaction_by_receipt_number(self, receipt_number: int) -> dict:
        """Fetch transaction by receipt number"""
        with get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM transactions WHERE receipt_number = ?",
                (receipt_number,)
            ).fetchone()
            if not row:
                raise ValueError(f"رسید نمبر {receipt_number} موجود نہیں ہے")
            return dict(row)
