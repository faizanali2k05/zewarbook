from src.repositories.db import get_connection


class PartyRepository:
    def add_party(self, payload: dict) -> int:
        with get_connection() as conn:
            cur = conn.execute(
                "INSERT INTO parties(type, name, phone, address) VALUES (:type, :name, :phone, :address)",
                payload,
            )
            return cur.lastrowid

    def list_parties(self, party_type: str | None = None):
        with get_connection() as conn:
            if party_type:
                return conn.execute("SELECT * FROM parties WHERE type = ? ORDER BY id DESC", (party_type,)).fetchall()
            return conn.execute("SELECT * FROM parties ORDER BY id DESC").fetchall()
