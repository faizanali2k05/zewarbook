from src.repositories.db import get_connection


class ItemRepository:
    def add_item(self, payload: dict) -> int:
        with get_connection() as conn:
            cur = conn.execute(
                """
                INSERT INTO items(sku, name_urdu, category, purity, weight, making_charges, stone_details, quantity, min_quantity)
                VALUES (:sku, :name_urdu, :category, :purity, :weight, :making_charges, :stone_details, :quantity, :min_quantity)
                """,
                payload,
            )
            return cur.lastrowid

    def list_items(self, query: str = ""):
        pattern = f"%{query}%"
        with get_connection() as conn:
            return conn.execute(
                "SELECT * FROM items WHERE sku LIKE ? OR name_urdu LIKE ? ORDER BY id DESC",
                (pattern, pattern),
            ).fetchall()

    def get_item(self, item_id: int):
        with get_connection() as conn:
            return conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()

    def update_item(self, item_id: int, payload: dict) -> None:
        with get_connection() as conn:
            conn.execute(
                """
                UPDATE items
                SET sku=:sku, name_urdu=:name_urdu, category=:category, purity=:purity, weight=:weight,
                    making_charges=:making_charges, stone_details=:stone_details, quantity=:quantity, min_quantity=:min_quantity
                WHERE id=:id
                """,
                {**payload, "id": item_id},
            )

    def delete_item(self, item_id: int) -> None:
        with get_connection() as conn:
            conn.execute("DELETE FROM items WHERE id = ?", (item_id,))

    def low_stock_items(self):
        with get_connection() as conn:
            return conn.execute("SELECT * FROM items WHERE quantity <= min_quantity ORDER BY quantity ASC").fetchall()
