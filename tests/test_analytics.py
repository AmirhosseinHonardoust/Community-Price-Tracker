from pathlib import Path

import pandas as pd
import pytest

import analytics
from dataframe_utils import require_columns
from db import connect, exec_script, qi

SCHEMA = Path(__file__).resolve().parents[1] / "src" / "schema.sql"


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


def test_load_prices_df_computes_unit_price(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    seed_db(db_path)
    monkeypatch.setattr(analytics, "connect", lambda: connect(db_path))
    df = analytics.load_prices_df()
    assert not df.empty
    assert sorted(df["unit_price"]) == [1.30, 1.50]


def test_plot_trend_writes_png(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    seed_db(db_path)
    monkeypatch.setattr(analytics, "connect", lambda: connect(db_path))
    df = analytics.load_prices_df()
    out = analytics.plot_trend(df, "Milk", tmp_path)
    assert out is not None
    assert out.exists()


def test_plot_trend_returns_none_for_missing_item(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    seed_db(db_path)
    monkeypatch.setattr(analytics, "connect", lambda: connect(db_path))
    df = analytics.load_prices_df()
    assert analytics.plot_trend(df, "Nonexistent", tmp_path) is None


def test_plot_basket_writes_png(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    seed_db(db_path)
    monkeypatch.setattr(analytics, "connect", lambda: connect(db_path))
    df = analytics.load_prices_df()
    out = analytics.plot_basket(df, ["Milk"], tmp_path)
    assert out is not None
    assert out.exists()


def test_require_columns_raises_on_missing():
    df = pd.DataFrame({"a": [1]})
    with pytest.raises(ValueError):
        require_columns(df, {"a", "b"}, "test context")
