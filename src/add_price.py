#!/usr/bin/env python3
"""CLI to log a single price observation."""

from __future__ import annotations

import argparse
import sqlite3
from datetime import date

from db import add_db_arg, connect, get_or_create_item, qi, resolve_db_path


def main() -> None:
    ap = argparse.ArgumentParser(description="Add a price observation.")
    ap.add_argument("--item", required=True, help="Item name (e.g., Milk)")
    ap.add_argument("--store-id", type=int, default=None, help="Existing store id (optional)")
    ap.add_argument("--price", type=float, required=True)
    ap.add_argument("--currency", default="USD")
    ap.add_argument("--quantity", type=float, default=1.0, help="How many units covered by price")
    ap.add_argument("--date", default=date.today().isoformat())
    add_db_arg(ap)
    args = ap.parse_args()

    # Validate up front with a clear message, rather than letting these fall
    # through to the DB's CHECK(price >= 0) constraint and a generic
    # IntegrityError that (misleadingly) always pointed at --store-id.
    if args.price < 0:
        raise SystemExit(f"--price must be >= 0, got {args.price}")
    if args.quantity <= 0:
        raise SystemExit(f"--quantity must be > 0, got {args.quantity}")

    with connect(resolve_db_path(args.db)) as con:
        item_id = get_or_create_item(con, args.item)
        try:
            qi(
                con,
                "INSERT INTO price(item_id, store_id, price, currency, quantity, date) "
                "VALUES(?,?,?,?,?,?)",
                (item_id, args.store_id, args.price, args.currency, args.quantity, args.date),
            )
        except sqlite3.IntegrityError as exc:
            # Any remaining IntegrityError at this point is a foreign-key
            # failure (price/quantity are already validated above), so it's
            # safe to point specifically at --store-id.
            raise SystemExit(
                f"Could not log price: {exc}. "
                f"Check that --store-id {args.store_id} exists (see list_data.py)."
            ) from exc
    print("Price logged ✅")


if __name__ == "__main__":
    main()
