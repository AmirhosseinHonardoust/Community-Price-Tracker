#!/usr/bin/env python3
"""Shared helpers for turning SQLite query results into validated DataFrames.

Kept separate from db.py so lightweight CLI scripts (add_item.py, add_store.py,
add_price.py, list_data.py) don't need to import pandas just to talk to SQLite.
"""

from __future__ import annotations

import sqlite3

import pandas as pd


def rows_to_df(rows: list[sqlite3.Row]) -> pd.DataFrame:
    """Convert sqlite3.Row results into a DataFrame with named columns."""
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame([dict(r) for r in rows])


def require_columns(df: pd.DataFrame, required: set[str], context: str) -> None:
    """Raise ValueError with a clear message if `df` is missing any required column."""
    missing = required - set(map(str, df.columns))
    if missing:
        raise ValueError(
            f"Missing expected columns in {context}: {sorted(missing)}. "
            f"Seen columns: {list(df.columns)}. "
            "Fix: delete data/prices.db, run src/init_db.py, then add prices again."
        )


def with_unit_price(df: pd.DataFrame) -> pd.DataFrame:
    """Return `df` with a `unit_price` column (price / quantity, 0-quantity -> NA).

    Shared by analytics.py and the Streamlit Trends/Basket tabs so the
    zero-quantity handling can't drift between the CLI and the UI.
    """
    df = df.copy()
    df["unit_price"] = df["price"] / df["quantity"].replace(0, pd.NA)
    return df
