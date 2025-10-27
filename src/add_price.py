#!/usr/bin/env python3
from __future__ import annotations
import argparse
from datetime import date
from db import connect, q, qi

def ensure_item(con, name: str):
    row = q(con, "SELECT id FROM item WHERE name=?", (name.strip(),))
    if row:
        return row[0]["id"]
    return qi(con, "INSERT INTO item(name, category, unit) VALUES(?, 'general', 'unit')", (name.strip(),)).lastrowid

def main() -> None:
    ap = argparse.ArgumentParser(description="Add a price observation.")
    ap.add_argument("--item", required=True, help="Item name (e.g., Milk)")
    ap.add_argument("--store-id", type=int, default=None, help="Existing store id (optional)")
    ap.add_argument("--price", type=float, required=True)
    ap.add_argument("--currency", default="USD")
    ap.add_argument("--quantity", type=float, default=1.0, help="How many units covered by price")
    ap.add_argument("--date", default=date.today().isoformat())
    args = ap.parse_args()

    with connect() as con:
        item_id = ensure_item(con, args.item)
        qi(con, "INSERT INTO price(item_id, store_id, price, currency, quantity, date) VALUES(?,?,?,?,?,?)",
           (item_id, args.store_id, args.price, args.currency, args.quantity, args.date))
    print("Price logged ✅")

if __name__ == "__main__":
    main()
