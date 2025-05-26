import pytest 

from pathlib import Path
from typing import Iterator

from guardian.db.sqlite import SQLiteManager


@pytest.fixture()
def sqlite_manager(tmp_path: Path) -> Iterator[SQLiteManager]:
    """Yields a fresh in-memory DB for every test function."""
    db_file = tmp_path / "guardian.sqlite3"
    with SQLiteManager(db_file) as manager:
        yield manager