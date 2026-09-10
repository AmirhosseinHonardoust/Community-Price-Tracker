#!/usr/bin/env python3
"""CLI to delete a single price observation by id (for fixing mis-entered data)."""

from __future__ import annotations

import argparse
import sqlite3

from db import add_db_arg, connect, resolve_db_path


def delete_price(con: sqlite3.Connection, price_id: int) -> bool:
    """Delete the price row with `price_id`. Returns True if a row was deleted."""
    cur = con.execute("DELETE FROM price WHERE id=?", (price_id,))
    con.commit()
    return cur.rowcount > 0


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Delete a price observation by id (see list_data.py for ids)."
    )
    ap.add_argument("--id", type=int, required=True, help="Price id to delete")
    add_db_arg(ap)
    args = ap.parse_args()

    with connect(resolve_db_path(args.db)) as con:
        deleted = delete_price(con, args.id)

    if deleted:
        print(f"Price id={args.id} deleted ✅")
    else:
        raise SystemExit(f"No price found with id={args.id}")


if __name__ == "__main__":
    main()
