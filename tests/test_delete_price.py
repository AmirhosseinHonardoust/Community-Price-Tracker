from pathlib import Path

import pytest

import delete_price
from db import connect, exec_script, q, qi

SCHEMA = Path(__file__).resolve().parents[1] / "src" / "schema.sql"


def make_db(tmp_path: Path) -> Path:
    db_path = tmp_path / "t.db"
    with connect(db_path) as con:
        exec_script(con, SCHEMA)
        qi(con, "INSERT INTO item(name, unit) VALUES('Milk','liter')")
        qi(
            con,
            "INSERT INTO price(item_id, store_id, price, currency, quantity, date) "
            "VALUES(1,NULL,1.30,'EUR',1,'2025-01-01')",
        )
    return db_path


def test_delete_price_function_removes_row(tmp_path):
    db_path = make_db(tmp_path)
    with connect(db_path) as con:
        price_id = q(con, "SELECT id FROM price")[0]["id"]
        assert delete_price.delete_price(con, price_id) is True
        assert q(con, "SELECT * FROM price") == []


def test_delete_price_function_returns_false_when_missing(tmp_path):
    db_path = make_db(tmp_path)
    with connect(db_path) as con:
        assert delete_price.delete_price(con, 9999) is False


def test_main_deletes_by_id(tmp_path, monkeypatch):
    db_path = make_db(tmp_path)
    with connect(db_path) as con:
        price_id = q(con, "SELECT id FROM price")[0]["id"]
    monkeypatch.setenv("CPT_DB_PATH", str(db_path))
    monkeypatch.setattr("sys.argv", ["delete_price.py", "--id", str(price_id)])
    delete_price.main()
    with connect(db_path) as con:
        assert q(con, "SELECT * FROM price") == []


def test_main_raises_for_unknown_id(tmp_path, monkeypatch):
    db_path = make_db(tmp_path)
    monkeypatch.setenv("CPT_DB_PATH", str(db_path))
    monkeypatch.setattr("sys.argv", ["delete_price.py", "--id", "9999"])
    with pytest.raises(SystemExit, match="No price found with id=9999"):
        delete_price.main()


def test_main_accepts_explicit_db_flag(tmp_path, monkeypatch):
    db_path = make_db(tmp_path)
    with connect(db_path) as con:
        price_id = q(con, "SELECT id FROM price")[0]["id"]
    monkeypatch.setattr(
        "sys.argv", ["delete_price.py", "--id", str(price_id), "--db", str(db_path)]
    )
    delete_price.main()
    with connect(db_path) as con:
        assert q(con, "SELECT * FROM price") == []
