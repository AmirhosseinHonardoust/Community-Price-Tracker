import csv
from pathlib import Path

import pytest

from db import connect, exec_script, q
from import_csv import main as import_main

SCHEMA = Path(__file__).resolve().parents[1] / "src" / "schema.sql"


def make_db(tmp_path: Path) -> Path:
    db_path = tmp_path / "test.db"
    with connect(db_path) as con:
        exec_script(con, SCHEMA)
    return db_path


def write_csv(tmp_path: Path, rows: list[list[str]]) -> Path:
    path = tmp_path / "prices.csv"
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["item", "unit", "store", "city", "price", "currency", "quantity", "date"])
        w.writerows(rows)
    return path


def test_import_csv_creates_items_stores_prices(tmp_path, monkeypatch):
    db_path = make_db(tmp_path)
    csv_path = write_csv(
        tmp_path,
        [
            ["Milk", "liter", "Market 1", "Helsinki", "1.30", "EUR", "1", "2025-01-01"],
            ["Milk", "liter", "Market 1", "Helsinki", "1.35", "EUR", "1", "2025-01-08"],
        ],
    )
    monkeypatch.setattr(
        "sys.argv", ["import_csv.py", "--db", str(db_path), "--file", str(csv_path)]
    )
    import_main()

    with connect(db_path) as con:
        items = q(con, "SELECT name FROM item")
        stores = q(con, "SELECT name, city FROM store")
        prices = q(con, "SELECT price FROM price ORDER BY date")

    assert [r["name"] for r in items] == ["Milk"]
    assert [dict(r) for r in stores] == [{"name": "Market 1", "city": "Helsinki"}]
    assert [r["price"] for r in prices] == [1.30, 1.35]


def test_import_csv_missing_required_column_exits(tmp_path, monkeypatch):
    db_path = make_db(tmp_path)
    bad_csv = tmp_path / "bad.csv"
    bad_csv.write_text("item,price\nMilk,1.3\n")
    monkeypatch.setattr("sys.argv", ["import_csv.py", "--db", str(db_path), "--file", str(bad_csv)])
    with pytest.raises(SystemExit):
        import_main()
