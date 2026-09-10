from pathlib import Path

import init_db
from db import connect


def test_init_db_creates_expected_tables(tmp_path, monkeypatch):
    db_path = tmp_path / "t.db"
    monkeypatch.setenv("CPT_DB_PATH", str(db_path))
    init_db.main()

    with connect(db_path) as con:
        tables = {
            r[0]
            for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        }
    assert {"item", "store", "price"} <= tables


def test_init_db_is_idempotent(tmp_path, monkeypatch):
    db_path = tmp_path / "t.db"
    monkeypatch.setenv("CPT_DB_PATH", str(db_path))
    init_db.main()
    init_db.main()  # should not raise even though tables already exist
    assert Path(db_path).exists()
