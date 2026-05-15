import bcrypt

from src.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self) -> None:
        self.repo = UserRepository()

    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))

    def ensure_default_admin(self) -> None:
        if not self.repo.get_by_username("admin"):
            self.repo.create_user("admin", self.hash_password("admin123"), "admin")

    def login(self, username: str, password: str):
        user = self.repo.get_by_username(username)
        if not user or not user["is_active"]:
            return None
        if self.verify_password(password, user["password_hash"]):
            return user
        return None
