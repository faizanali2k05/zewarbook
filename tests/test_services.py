import tempfile
import unittest
from pathlib import Path

from src.repositories.db import get_connection


class RepositorySmokeTests(unittest.TestCase):
    def test_connection_roundtrip(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as td:
            db_path = Path(td) / "tmp.db"
            conn = get_connection(db_path)
            try:
                conn.execute("CREATE TABLE sample(id INTEGER PRIMARY KEY, name TEXT)")
                conn.execute("INSERT INTO sample(name) VALUES ('ok')")
                row = conn.execute("SELECT COUNT(*) AS c FROM sample").fetchone()
                self.assertEqual(row["c"], 1)
            finally:
                conn.close()


if __name__ == "__main__":
    unittest.main()
