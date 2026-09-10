from pathlib import Path

from db import connect, exec_script, get_or_create_item, get_or_create_store, price_rows, q, qi

SCHEMA = Path(__file__).resolve().parents[1] / "src" / "schema.sql"


def make_db(tmp_path: Path) -> Path:
    db_path = tmp_path / "test.db"
    with connect(db_path) as con:
        exec_script(con, SCHEMA)
    return db_path


def test_connect_enables_foreign_keys(tmp_path):
    db_path = make_db(tmp_path)
    with connect(db_path) as con:
        row = con.execute("PRAGMA foreign_keys").fetchone()
        assert row[0] == 1


def test_q_and_qi_roundtrip(tmp_path):
    db_path = make_db(tmp_path)
    with connect(db_path) as con:
        qi(con, "INSERT INTO item(name, unit) VALUES(?, ?)", ("Milk", "liter"))
        rows = q(con, "SELECT name, unit FROM item")
    assert [dict(r) for r in rows] == [{"name": "Milk", "unit": "liter"}]


def test_get_or_create_item_is_idempotent(tmp_path):
    db_path = make_db(tmp_path)
    with connect(db_path) as con:
        id1 = get_or_create_item(con, "Bread", "loaf")
        id2 = get_or_create_item(con, "Bread", "loaf")
    assert id1 == id2


def test_get_or_create_item_backfills_empty_unit(tmp_path):
    db_path = make_db(tmp_path)
    with connect(db_path) as con:
        qi(con, "INSERT INTO item(name, unit) VALUES(?, ?)", ("Eggs", ""))
        item_id = get_or_create_item(con, "Eggs", "dozen")
        unit = q(con, "SELECT unit FROM item WHERE id=?", (item_id,))[0]["unit"]
    assert unit == "dozen"


def test_get_or_create_item_uses_category_only_on_create(tmp_path):
    db_path = make_db(tmp_path)
    with connect(db_path) as con:
        item_id = get_or_create_item(con, "Coffee", "pack", "beverage")
        category = q(con, "SELECT category FROM item WHERE id=?", (item_id,))[0]["category"]
    assert category == "beverage"


def test_get_or_create_store_dedupes_by_name_and_city(tmp_path):
    db_path = make_db(tmp_path)
    with connect(db_path) as con:
        id1 = get_or_create_store(con, "Market 1", "Helsinki")
        id2 = get_or_create_store(con, "Market 1", "Helsinki")
        id3 = get_or_create_store(con, "Market 1", "Berlin")
    assert id1 == id2
    assert id1 != id3


def test_get_or_create_store_returns_none_for_blank_name(tmp_path):
    db_path = make_db(tmp_path)
    with connect(db_path) as con:
        assert get_or_create_store(con, "", "Helsinki") is None
        assert get_or_create_store(con, None, "Helsinki") is None


def _seed_prices(con) -> None:
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


def test_price_rows_no_filter_returns_everything(tmp_path):
    db_path = make_db(tmp_path)
    with connect(db_path) as con:
        _seed_prices(con)
        rows = price_rows(con)
    assert {r["item"] for r in rows} == {"Milk", "Bread"}


def test_price_rows_item_names_filters_case_insensitively(tmp_path):
    db_path = make_db(tmp_path)
    with connect(db_path) as con:
        _seed_prices(con)
        rows = price_rows(con, item_names=["milk"])
    assert [r["item"] for r in rows] == ["Milk"]


def test_price_rows_city_filters_case_insensitively(tmp_path):
    db_path = make_db(tmp_path)
    with connect(db_path) as con:
        _seed_prices(con)
        rows = price_rows(con, city="berlin")
    assert [r["item"] for r in rows] == ["Bread"]


def test_price_rows_limit_caps_row_count(tmp_path):
    db_path = make_db(tmp_path)
    with connect(db_path) as con:
        _seed_prices(con)
        rows = price_rows(con, limit=1)
    assert len(rows) == 1
