from pathlib import Path

import list_data
from db import connect, exec_script, q, qi
from list_data import _as_dicts

SCHEMA = Path(__file__).resolve().parents[1] / "src" / "schema.sql"


def test_as_dicts_produces_named_columns(tmp_path):
    """Regression test: tabulate(rows, headers='keys') needs dicts, not sqlite3.Row,
    or it silently falls back to positional 0/1/2 headers."""
    db_path = tmp_path / "t.db"
    with connect(db_path) as con:
        exec_script(con, SCHEMA)
        qi(con, "INSERT INTO item(name, unit) VALUES('Milk','liter')")
        rows = q(con, "SELECT id, name, unit FROM item")

    result = _as_dicts(rows)

    assert result == [{"id": 1, "name": "Milk", "unit": "liter"}]
    assert list(result[0].keys()) == ["id", "name", "unit"]


def test_list_data_main_prints_named_headers(tmp_path, monkeypatch, capsys):
    db_path = tmp_path / "t.db"
    with connect(db_path) as con:
        exec_script(con, SCHEMA)
        qi(con, "INSERT INTO item(name, unit) VALUES('Milk','liter')")

    monkeypatch.setattr("sys.argv", ["list_data.py", "--db", str(db_path)])
    list_data.main()

    out = capsys.readouterr().out
    assert "Milk" in out
    # Real column names as headers, not tabulate's positional 0/1/2/3 fallback.
    assert "name" in out and "category" in out and "unit" in out
    assert "| 0 " not in out


def _seed_multi_city(db_path: Path) -> None:
    with connect(db_path) as con:
        exec_script(con, SCHEMA)
        qi(con, "INSERT INTO item(name, unit) VALUES('Milk','liter')")
        qi(con, "INSERT INTO item(name, unit) VALUES('Bread','loaf')")
        qi(con, "INSERT INTO store(name, city) VALUES('Market 1','Helsinki')")
        qi(con, "INSERT INTO store(name, city) VALUES('Market 2','Berlin')")
        qi(
            con,
            "INSERT INTO price(item_id,store_id,price,currency,quantity,date) "
            "VALUES(1,1,1.3,'EUR',1,'2025-01-01')",
        )
        qi(
            con,
            "INSERT INTO price(item_id,store_id,price,currency,quantity,date) "
            "VALUES(2,2,2.1,'EUR',1,'2025-01-02')",
        )


def test_list_data_item_filter_restricts_prices(tmp_path, monkeypatch, capsys):
    db_path = tmp_path / "t.db"
    _seed_multi_city(db_path)
    monkeypatch.setattr("sys.argv", ["list_data.py", "--db", str(db_path), "--item", "Milk"])
    list_data.main()
    out = capsys.readouterr().out
    assert "Milk" in out
    assert "Bread" not in out.split("Prices")[1]


def test_list_data_city_filter_restricts_prices(tmp_path, monkeypatch, capsys):
    db_path = tmp_path / "t.db"
    _seed_multi_city(db_path)
    monkeypatch.setattr("sys.argv", ["list_data.py", "--db", str(db_path), "--city", "Berlin"])
    list_data.main()
    out = capsys.readouterr().out
    prices_section = out.split("Prices")[1]
    assert "Bread" in prices_section
    assert "Milk" not in prices_section


def test_list_data_limit_restricts_row_count(tmp_path, monkeypatch, capsys):
    db_path = tmp_path / "t.db"
    _seed_multi_city(db_path)
    monkeypatch.setattr("sys.argv", ["list_data.py", "--db", str(db_path), "--limit", "1"])
    list_data.main()
    prices_section = capsys.readouterr().out.split("Prices")[1]
    # Only the most recent row (2025-01-02, Bread) should appear.
    assert "Bread" in prices_section
    assert "Milk" not in prices_section


def test_list_data_main_handles_empty_db(tmp_path, monkeypatch, capsys):
    db_path = tmp_path / "t.db"
    with connect(db_path) as con:
        exec_script(con, SCHEMA)

    monkeypatch.setattr("sys.argv", ["list_data.py", "--db", str(db_path)])
    list_data.main()  # should not raise on empty tables

    out = capsys.readouterr().out
    assert "Items" in out
    assert "Stores" in out
    assert "Prices" in out
