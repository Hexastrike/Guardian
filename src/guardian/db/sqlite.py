from __future__ import annotations

import sqlite3
import logging
import hashlib

from pathlib import Path
from typing import Any, Optional


class SQLiteManager:
    """
    Wrapper around SQLite for storing VT JSON results

    Opens a single connection on construction and reuses it everywhere
    Exposes context-manager helpers
    """

    def __init__(
        self,
        db_path: Path,
        *,
        # Allow the caller to set pragmas (e.g. WAL mode) up front if desired
        pragmas: Optional[dict[str, Any]] = None,
        # Pass through to sqlite3.connect when you need different isolation
        isolation_level: str | None = None,
    ) -> None:
        self._db_path = db_path
        self._db_path.touch(exist_ok=True)

        # One connection for the whole object
        self._conn = sqlite3.connect(
            self._db_path,
            isolation_level=isolation_level,
            check_same_thread=False, # lets us use threads safely
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
        )
        self._conn.row_factory = sqlite3.Row

        # Apply optional PRAGMAs (e.g. {"journal_mode": "wal"})
        if pragmas:
            for key, value in pragmas.items():
                self._conn.execute(f"PRAGMA {key}={value}")

        logging.debug("Opened SQLite connection: %s", self._db_path)

    # Context-manager helpers
    def __enter__(self) -> "SQLiteManager":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def close(self) -> None:
        """Explicitly close the underlying connection."""
        try:
            self._conn.close()
            logging.debug("Closed SQLite connection: %s", self._db_path)
        except Exception as exc:
            logging.error("Error while closing SQLite connection: %s", exc)

    # Public API
    def sanity_check(self) -> None:
        """Abort early if the DB file is unusable."""
        self._conn.execute("SELECT 1") # will raise if corrupt
        logging.info("SQLite ready: %s", self._db_path)

    # Internal helpers
    @staticmethod
    def _hash_name(entity: str) -> str:
        md5 = hashlib.md5(entity.encode(), usedforsecurity=False)
        return f"vt_{md5.hexdigest()}"

    # DDL + DML
    def ensure_table(self, entity: str) -> str:
        """Create (if missing) and return the per-entity table name."""
        table = self._hash_name(entity)
        ddl = f"""
            CREATE TABLE IF NOT EXISTS {table} (
              id               INTEGER PRIMARY KEY AUTOINCREMENT,
              vt_resource_id   TEXT NOT NULL UNIQUE,
              vt_resource_type TEXT,
              created_at       DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """
        self._conn.executescript(ddl)
        return table

    def insert(self, table: str, vt_resource_id: str, vt_resource_type: str) -> bool:
        """
        Insert VT result; returns True if actually inserted (i.e. not ignored).
        """
        try:
            cur = self._conn.execute(
                f"""
                INSERT OR IGNORE INTO {table} (vt_resource_id, vt_resource_type)
                VALUES (?, ?)
                """,
                (vt_resource_id, vt_resource_type),
            )
            self._conn.commit()
            return cur.rowcount > 0

        except Exception as exc:
            logging.error(
                "Failed to insert VT result %s into %s: %s",
                vt_resource_id,
                table,
                exc,
            )
            return False