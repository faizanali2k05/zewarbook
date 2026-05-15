from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "jewelry_inventory.db"
BACKUP_DIR = DATA_DIR / "backups"
REPORT_DIR = DATA_DIR / "reports"
DEFAULT_FONT_FAMILY = "Noto Nastaliq Urdu"
DEFAULT_FONT_SIZE = 11

for directory in (DATA_DIR, BACKUP_DIR, REPORT_DIR):
    directory.mkdir(parents=True, exist_ok=True)
