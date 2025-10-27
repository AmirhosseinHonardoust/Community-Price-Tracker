#!/usr/bin/env python3
from __future__ import annotations
import argparse
from db import connect, qi

def main() -> None:
    ap = argparse.ArgumentParser(description="Add a new item (e.g., Bread, Milk).")
    ap.add_argument("--name", required=True)
    ap.add_argument("--category", default="general")
    ap.add_argument("--unit", default="unit", help="kg, liter, loaf, dozen, etc.")
    args = ap.parse_args()

    with connect() as con:
        rowid = qi(con, "INSERT OR IGNORE INTO item(name, category, unit) VALUES(?,?,?)",
                   (args.name.strip(), args.category.strip(), args.unit.strip())).lastrowid
    print(f"Item added (or already existed). id={rowid if rowid else 'existing'} ✅")

if __name__ == "__main__":
    main()
