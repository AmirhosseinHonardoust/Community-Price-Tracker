from pathlib import Path

from streamlit.testing.v1 import AppTest

from db import connect, exec_script, qi

SCHEMA = Path(__file__).resolve().parents[1] / "src" / "schema.sql"
APP = str(Path(__file__).resolve().parents[1] / "src" / "streamlit_app.py")


def seed_db(db_path: Path) -> None:
    with connect(db_path) as con:
        exec_script(con, SCHEMA)
        qi(con, "INSERT INTO item(name, unit) VALUES('Milk','liter')")
        qi(con, "INSERT INTO store(name, city) VALUES('Market 1','Helsinki')")
        qi(
            con,
            "INSERT INTO price(item_id, store_id, price, currency, quantity, date) "
            "VALUES(1,1,1.30,'EUR',1,'2025-01-01')",
        )
        qi(
            con,
            "INSERT INTO price(item_id, store_id, price, currency, quantity, date) "
            "VALUES(1,1,1.50,'EUR',1,'2025-02-01')",
        )


def run_app(db_path: Path, monkeypatch) -> AppTest:
    monkeypatch.setenv("CPT_DB_PATH", str(db_path))
    at = AppTest.from_file(APP)
    at.run()
    return at


def test_app_loads_with_four_tabs(tmp_path, monkeypatch):
    db_path = tmp_path / "t.db"
    seed_db(db_path)
    at = run_app(db_path, monkeypatch)
    assert not at.exception
    assert [t.label for t in at.tabs] == ["Log Price", "Items & Stores", "Trends", "Basket"]


def test_log_price_for_existing_item_writes_to_db(tmp_path, monkeypatch):
    db_path = tmp_path / "t.db"
    seed_db(db_path)
    at = run_app(db_path, monkeypatch)

    at.selectbox(key="item_select").select("Milk (liter)")
    at.number_input(key="price").set_value(1.42)
    at.text_input(key="currency").set_value("EUR")
    at.run()
    at.button(key="save_price_btn").click()
    at.run()

    assert not at.exception
    with connect(db_path) as con:
        rows = con.execute(
            "SELECT price, currency FROM price WHERE price=1.42 AND currency='EUR'"
        ).fetchall()
    assert len(rows) == 1


def test_log_price_with_new_item_and_store_creates_both(tmp_path, monkeypatch):
    db_path = tmp_path / "t.db"
    seed_db(db_path)
    at = run_app(db_path, monkeypatch)

    at.text_input(key="new_item").set_value("Yogurt")
    at.text_input(key="new_store").set_value("Corner Shop")
    at.text_input(key="new_city").set_value("Berlin")
    at.number_input(key="price").set_value(2.10)
    at.run()
    at.button(key="save_price_btn").click()
    at.run()

    assert not at.exception
    with connect(db_path) as con:
        item = con.execute("SELECT id FROM item WHERE name='Yogurt'").fetchone()
        store = con.execute("SELECT id FROM store WHERE name='Corner Shop'").fetchone()
        assert item is not None
        assert store is not None
        price_row = con.execute(
            "SELECT * FROM price WHERE item_id=? AND store_id=?", (item[0], store[0])
        ).fetchone()
        assert price_row is not None


def test_log_price_without_item_selection_shows_error(tmp_path, monkeypatch):
    db_path = tmp_path / "t.db"
    seed_db(db_path)
    at = run_app(db_path, monkeypatch)

    at.button(key="save_price_btn").click()
    at.run()

    assert not at.exception
    assert any("Choose an existing item" in e.value for e in at.error)


def test_items_and_stores_tab_renders_without_error(tmp_path, monkeypatch):
    db_path = tmp_path / "t.db"
    seed_db(db_path)
    at = run_app(db_path, monkeypatch)
    assert not at.exception
    assert len(at.dataframe) >= 3  # items, stores, prices


def test_trends_tab_shows_no_warning_for_known_item(tmp_path, monkeypatch):
    db_path = tmp_path / "t.db"
    seed_db(db_path)
    at = run_app(db_path, monkeypatch)

    at.text_input(key="trend_item").set_value("Milk")
    at.run()
    at.button(key="show_trend_btn").click()
    at.run()

    assert not at.exception
    assert len(at.warning) == 0


def test_trends_tab_warns_for_unknown_item(tmp_path, monkeypatch):
    db_path = tmp_path / "t.db"
    seed_db(db_path)
    at = run_app(db_path, monkeypatch)

    at.text_input(key="trend_item").set_value("Nonexistent")
    at.run()
    at.button(key="show_trend_btn").click()
    at.run()

    assert not at.exception
    assert any("No data" in w.value for w in at.warning)


def test_basket_tab_shows_no_warning_for_known_item(tmp_path, monkeypatch):
    db_path = tmp_path / "t.db"
    seed_db(db_path)
    at = run_app(db_path, monkeypatch)

    at.text_input(key="basket_items_input").set_value("Milk")
    at.run()
    at.button(key="compare_basket_btn").click()
    at.run()

    assert not at.exception
    assert len(at.warning) == 0


def test_basket_tab_warns_for_empty_input(tmp_path, monkeypatch):
    db_path = tmp_path / "t.db"
    seed_db(db_path)
    at = run_app(db_path, monkeypatch)

    at.text_input(key="basket_items_input").set_value("   ")
    at.run()
    at.button(key="compare_basket_btn").click()
    at.run()

    assert not at.exception
    assert any("Enter at least one item" in w.value for w in at.warning)
