#!/usr/bin/env python3
from __future__ import annotations
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "prices.db"

def connect(db_path: Path | None = None) -> sqlite3.Connection:
    p = db_path or DB_PATH
    p.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(p)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON;")
    return con

def exec_script(con: sqlite3.Connection, sql_path: Path) -> None:
    con.executescript(sql_path.read_text(encoding="utf-8"))

def q(con: sqlite3.Connection, sql: str, params: tuple = ()) -> list[sqlite3.Row]:
    return con.execute(sql, params).fetchall()

def qi(con: sqlite3.Connection, sql: str, params: tuple = ()) -> sqlite3.Cursor:
    cur = con.execute(sql, params)
    con.commit()
    return cur
