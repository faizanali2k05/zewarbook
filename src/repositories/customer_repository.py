from src.repositories.db import get_connection


class CustomerRepository:
    def add(self, name: str, mobile: str = "", address: str = "", code: str | None = None) -> int:
        with get_connection() as conn:
            cur = conn.execute(
                """
                INSERT INTO customers (code, name, mobile, address)
                VALUES (?, ?, ?, ?)
                """,
                (code, name, mobile, address),
            )
            return cur.lastrowid

    def get(self, customer_id: int):
        with get_connection() as conn:
            return conn.execute(
                "SELECT * FROM customers WHERE id = ?", (customer_id,)
            ).fetchone()

    def get_by_code(self, code: str):
        with get_connection() as conn:
            return conn.execute(
                "SELECT * FROM customers WHERE code = ?", (code,)
            ).fetchone()

    def search(self, query: str):
        pattern = f"%{query}%"
        with get_connection() as conn:
            return conn.execute(
                """
                SELECT * FROM customers
                WHERE name LIKE ? OR mobile LIKE ? OR code LIKE ?
                ORDER BY name
                """,
                (pattern, pattern, pattern),
            ).fetchall()

    def list_all(self):
        with get_connection() as conn:
            return conn.execute(
                "SELECT * FROM customers ORDER BY id"
            ).fetchall()

    def update(self, customer_id: int, name: str, mobile: str = "", address: str = "") -> int:
        with get_connection() as conn:
            cur = conn.execute(
                """
                UPDATE customers
                SET name = ?, mobile = ?, address = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (name, mobile, address, customer_id),
            )
            return cur.rowcount
