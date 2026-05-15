import shutil
from datetime import datetime

from config.settings import BACKUP_DIR, DB_PATH
from src.repositories.db import get_connection


class BackupService:
    def create_backup(self, user_id: int | None = None) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"inventory_backup_{timestamp}.db"
        backup_path = BACKUP_DIR / file_name
        shutil.copy2(DB_PATH, backup_path)
        with get_connection() as conn:
            conn.execute("INSERT INTO backups_log(file_name, created_by) VALUES (?, ?)", (file_name, user_id))
        return str(backup_path)

    def restore_backup(self, backup_file: str) -> None:
        shutil.copy2(backup_file, DB_PATH)
