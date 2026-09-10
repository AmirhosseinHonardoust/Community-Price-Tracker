#!/usr/bin/env python3
"""Print the current contents of the item, store, and price tables."""

from __future__ import annotations

import argparse
import sqlite3

from tabulate import tabulate

from db import add_db_arg, connect, q, resolve_db_path


def _as_dicts(rows: list[sqlite3.Row]) -> list[dict]:
    """Convert sqlite3.Row objects to plain dicts.

    tabulate's headers="keys" only reads column names from dict-like rows;
    passing sqlite3.Row objects directly makes it fall back to positional
    0/1/2/3 headers instead of the real column names.
    """
    return [dict(r) for r in rows]


def main() -> None:
    ap = argparse.ArgumentParser(description="Print items, stores, and prices tables.")
    add_db_arg(ap)
    args = ap.parse_args()

    with connect(resolve_db_path(args.db)) as con:
        items = q(con, "SELECT * FROM item ORDER BY name")
        stores = q(con, "SELECT * FROM store ORDER BY name")
        prices = q(
            con,
            "SELECT p.id, i.name AS item, i.unit, s.name AS store, s.city, "
            "p.price, p.currency, p.quantity, p.date "
            "FROM price p LEFT JOIN item i ON i.id=p.item_id "
            "LEFT JOIN store s ON s.id=p.store_id ORDER BY p.date DESC, i.name",
        )
    print("\nItems")
    print(tabulate(_as_dicts(items), headers="keys", tablefmt="github"))
    print("\nStores")
    print(tabulate(_as_dicts(stores), headers="keys", tablefmt="github"))
    print("\nPrices")
    print(tabulate(_as_dicts(prices), headers="keys", tablefmt="github"))


if __name__ == "__main__":
    main()
