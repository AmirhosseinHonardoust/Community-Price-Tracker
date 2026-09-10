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


def resolve_db_path(db_arg: str | None) -> Path | None:
    """Turn an optional --db CLI value into a Path, or None to use the default."""
    return Path(db_arg) if db_arg else None


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
