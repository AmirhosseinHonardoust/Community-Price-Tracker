from pathlib import Path

import pytest

import add_item
import add_price
import add_store
from db import connect, exec_script, q

SCHEMA = Path(__file__).resolve().parents[1] / "src" / "schema.sql"


def init_db(db_path: Path) -> None:
    with connect(db_path) as con:
        exec_script(con, SCHEMA)


def test_add_item_is_idempotent(tmp_path, monkeypatch):
    db_path = tmp_path / "t.db"
    init_db(db_path)
    monkeypatch.setenv("CPT_DB_PATH", str(db_path))
    monkeypatch.setattr("sys.argv", ["add_item.py", "--name", "Milk", "--unit", "liter"])
    add_item.main()
    add_item.main()
    with connect(db_path) as con:
        rows = q(con, "SELECT * FROM item WHERE name='Milk'")
    assert len(rows) == 1


def test_add_store_is_idempotent(tmp_path, monkeypatch):
    db_path = tmp_path / "t.db"
    init_db(db_path)
    monkeypatch.setenv("CPT_DB_PATH", str(db_path))
    monkeypatch.setattr("sys.argv", ["add_store.py", "--name", "Market 1", "--city", "Helsinki"])
    add_store.main()
    add_store.main()
    with connect(db_path) as con:
        rows = q(con, "SELECT * FROM store WHERE name='Market 1'")
    assert len(rows) == 1


def test_add_price_raises_friendly_error_on_bad_store_id(tmp_path, monkeypatch):
    db_path = tmp_path / "t.db"
    init_db(db_path)
    monkeypatch.setenv("CPT_DB_PATH", str(db_path))
    monkeypatch.setattr(
        "sys.argv",
        ["add_price.py", "--item", "Milk", "--store-id", "9999", "--price", "1.5"],
    )
    with pytest.raises(SystemExit, match="Could not log price"):
        add_price.main()


def test_add_price_logs_successfully(tmp_path, monkeypatch):
    db_path = tmp_path / "t.db"
    init_db(db_path)
    monkeypatch.setenv("CPT_DB_PATH", str(db_path))
    monkeypatch.setattr(
        "sys.argv", ["add_price.py", "--item", "Milk", "--price", "1.35", "--currency", "EUR"]
    )
    add_price.main()
    with connect(db_path) as con:
        rows = q(con, "SELECT price, currency FROM price")
    assert [dict(r) for r in rows] == [{"price": 1.35, "currency": "EUR"}]
