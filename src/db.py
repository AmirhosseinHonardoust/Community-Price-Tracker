#!/usr/bin/env python3
"""SQLite connection and query helpers shared across the CLI tools."""

from __future__ import annotations

import argparse
import os
import sqlite3
from pathlib import Path

DEFAULT_DB_PATH = Path(__file__).resolve().parents[1] / "data" / "prices.db"


def _default_db_path() -> Path:
    """Resolve the DB path, honoring the CPT_DB_PATH env var override."""
    override = os.environ.get("CPT_DB_PATH")
    return Path(override) if override else DEFAULT_DB_PATH


def add_db_arg(parser: argparse.ArgumentParser) -> None:
    """Add a shared --db flag to `parser`.

    Precedence when omitted: CPT_DB_PATH env var, then DEFAULT_DB_PATH
    (<repo_root>/data/prices.db). Every CLI script uses this so `--db` behaves
    identically everywhere instead of each script inventing its own default.
    """
    parser.add_argument(
        "--db",
        default=None,
        help=f"Path to SQLite DB (default: $CPT_DB_PATH or {DEFAULT_DB_PATH})",
    )


def resolve_db_path(db_arg: str | None) -> Path:
    """Turn an optional --db CLI value into a concrete Path.

    Precedence when `db_arg` is falsy: CPT_DB_PATH env var, then DEFAULT_DB_PATH.
    Centralizing this here (instead of leaving it to `connect`'s internal
    fallback) lets callers that need the path *before* opening a connection
    (e.g. import_csv.py checking existence) still honor CPT_DB_PATH.
    """
    return Path(db_arg) if db_arg else _default_db_path()


def connect(db_path: Path | None = None) -> sqlite3.Connection:
    """Open a SQLite connection, creating parent dirs and enabling foreign keys."""
    p = db_path or _default_db_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(p)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON;")
    return con


def exec_script(con: sqlite3.Connection, sql_path: Path) -> None:
    """Execute a .sql file's statements against an open connection."""
    con.executescript(sql_path.read_text(encoding="utf-8"))


def q(con: sqlite3.Connection, sql: str, params: tuple = ()) -> list[sqlite3.Row]:
    """Run a SELECT and return all matching rows."""
    return con.execute(sql, params).fetchall()


def qi(con: sqlite3.Connection, sql: str, params: tuple = ()) -> sqlite3.Cursor:
    """Run an INSERT/UPDATE/DELETE, commit, and return the cursor."""
    cur = con.execute(sql, params)
    con.commit()
    return cur


def get_or_create_item(
    con: sqlite3.Connection, name: str, unit: str = "unit", category: str = "general"
) -> int:
    """Return the id of the item named `name`, creating it if needed.

    If the item already exists and its stored unit is empty, backfill it
    from `unit`. `category` is only used when creating a new row.
    """
    name = name.strip()
    row = con.execute("SELECT id FROM item WHERE name=?", (name,)).fetchone()
    if row:
        if unit and unit.strip():
            con.execute(
                "UPDATE item SET unit=COALESCE(NULLIF(unit,''), ?) WHERE id=?",
                (unit.strip(), row["id"]),
            )
            con.commit()
        return int(row["id"])
    cur = con.execute(
        "INSERT INTO item(name, category, unit) VALUES(?, ?, ?)",
        (name, (category or "general").strip() or "general", unit.strip() or "unit"),
    )
    con.commit()
    assert cur.lastrowid is not None
    return cur.lastrowid


PRICE_JOIN_SQL = """
    SELECT
      p.id,
      i.name AS item,
      i.unit AS unit,
      s.name AS store,
      s.city AS city,
      p.price AS price,
      p.currency AS currency,
      p.quantity AS quantity,
      p.date AS date
    FROM price p
    LEFT JOIN item i ON i.id = p.item_id
    LEFT JOIN store s ON s.id = p.store_id
"""


def price_rows(
    con: sqlite3.Connection,
    item_names: list[str] | None = None,
    city: str | None = None,
    order_by: str = "p.date DESC, i.name",
    limit: int | None = None,
) -> list[sqlite3.Row]:
    """Run the shared item/store/price join, used by list_data, analytics, and the
    Streamlit app so the query and column names live in exactly one place.

    `item_names`, when given, case-insensitively filters to those item names
    (used by the Streamlit Trends/Basket tabs and list_data's --item flag).
    `city` case-insensitively filters to one city (list_data's --city flag).
    `order_by` and `limit` are trusted internal constants, never user input,
    so it's safe to splice them into the SQL string directly.
    """
    sql = PRICE_JOIN_SQL
    conditions = []
    params: list[str] = []
    if item_names:
        placeholders = ",".join("?" * len(item_names))
        conditions.append(f"lower(i.name) IN ({placeholders})")
        params.extend(x.lower() for x in item_names)
    if city:
        conditions.append("lower(s.city) = lower(?)")
        params.append(city)
    if conditions:
        sql += " WHERE " + " AND ".join(conditions)
    if order_by:
        sql += f" ORDER BY {order_by}"
    if limit:
        sql += f" LIMIT {int(limit)}"
    return q(con, sql, tuple(params))


def get_or_create_store(
    con: sqlite3.Connection, name: str | None, city: str | None = None
) -> int | None:
    """Return the id of the (name, city) store, creating it if needed.

    Returns None if `name` is blank, since store is optional in the schema.
    """
    if not name or not name.strip():
        return None
    name = name.strip()
    city = (city or "").strip()
    row = con.execute(
        "SELECT id FROM store WHERE name=? AND COALESCE(city,'')=?",
        (name, city),
    ).fetchone()
    if row:
        return int(row["id"])
    cur = con.execute(
        "INSERT INTO store(name, city) VALUES(?, ?)",
        (name, city or None),
    )
    con.commit()
    return cur.lastrowid
