#!/usr/bin/env python3
"""CLI to add a new item (e.g., Bread, Milk). Idempotent by name."""

from __future__ import annotations

import argparse

from db import connect, get_or_create_item


def main() -> None:
    ap = argparse.ArgumentParser(description="Add a new item (e.g., Bread, Milk).")
    ap.add_argument("--name", required=True)
    ap.add_argument("--category", default="general")
    ap.add_argument("--unit", default="unit", help="kg, liter, loaf, dozen, etc.")
    args = ap.parse_args()

    with connect() as con:
        item_id = get_or_create_item(con, args.name, args.unit, args.category)
    print(f"Item ready with id={item_id} ✅")


if __name__ == "__main__":
    main()
