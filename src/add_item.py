#!/usr/bin/env python3
"""CLI to add a new item (e.g., Bread, Milk). Idempotent by name."""

from __future__ import annotations

import argparse

from db import add_db_arg, connect, get_or_create_item, resolve_db_path


def main() -> None:
    ap = argparse.ArgumentParser(description="Add a new item (e.g., Bread, Milk).")
    ap.add_argument("--name", required=True)
    ap.add_argument("--category", default="general")
    ap.add_argument("--unit", default="unit", help="kg, liter, loaf, dozen, etc.")
    add_db_arg(ap)
    args = ap.parse_args()

    with connect(resolve_db_path(args.db)) as con:
        item_id = get_or_create_item(con, args.name, args.unit, args.category)
    print(f"Item ready with id={item_id} ✅")


if __name__ == "__main__":
    main()
