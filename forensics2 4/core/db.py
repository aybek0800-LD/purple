"""
SafeDB — безопасное чтение SQLite-файлов браузеров.
Браузер блокирует БД пока открыт, поэтому копируем во временную папку.
"""

import shutil
import sqlite3
import tempfile
import logging
from pathlib import Path

log = logging.getLogger("forensics.db")


class SafeDB:
    """Копирует SQLite во временный файл и выполняет запрос."""

    def __init__(self):
        self._tmp_dir = tempfile.mkdtemp(prefix="forensics_")

    def query(self, db_path: str | Path, sql: str, limit: int = 500) -> list[tuple]:
        db_path = Path(db_path)
        if not db_path.exists():
            return []
        try:
            tmp = Path(self._tmp_dir) / (db_path.name + "_copy")
            shutil.copy2(db_path, tmp)
            with sqlite3.connect(tmp) as conn:
                conn.row_factory = sqlite3.Row
                return conn.execute(sql).fetchmany(limit)
        except Exception as e:
            log.debug("DB error (%s): %s", db_path.name, e)
            return []

    def cleanup(self) -> None:
        shutil.rmtree(self._tmp_dir, ignore_errors=True)

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.cleanup()
