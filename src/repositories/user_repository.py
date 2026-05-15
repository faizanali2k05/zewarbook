from src.repositories.db import get_connection


class UserRepository:
    def create_user(self, username: str, password_hash: str, role: str = "operator") -> int:
        with get_connection() as conn:
            cur = conn.execute(
                "INSERT INTO users(username, password_hash, role) VALUES (?, ?, ?)",
                (username, password_hash, role),
            )
            return cur.lastrowid

    def get_by_username(self, username: str):
        with get_connection() as conn:
            return conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
