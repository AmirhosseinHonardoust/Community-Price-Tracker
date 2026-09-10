#!/usr/bin/env python3
"""Import a denormalized price CSV into the normalized SQLite schema."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from db import (
    DEFAULT_DB_PATH,
    add_db_arg,
    connect,
    get_or_create_item,
    get_or_create_store,
    resolve_db_path,
)

REQ_COLS = {"item", "unit", "store", "city", "price", "currency", "quantity", "date"}


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Import denormalized CSV into normalized SQLite schema."
    )
    add_db_arg(ap)
    ap.add_argument(
        "--file",
        required=True,
        help="CSV with columns: item,unit,store,city,price,currency,quantity,date",
    )
    ap.add_argument("--limit", type=int, default=None, help="Import only first N rows (optional)")
    args = ap.parse_args()

    # BEHAVIOR CHANGE: --db previously defaulted to the cwd-relative "data/prices.db",
    # inconsistent with every other script's repo-root-relative default. Now aligned
    # via the shared add_db_arg/resolve_db_path (CPT_DB_PATH env var, else DEFAULT_DB_PATH).
    db_path = resolve_db_path(args.db) or DEFAULT_DB_PATH
    csv_path = Path(args.file)
    if not db_path.exists():
        raise SystemExit(f"DB not found: {db_path}. Run: python src/init_db.py")
    if not csv_path.exists():
        raise SystemExit(f"CSV not found: {csv_path}")

    df = pd.read_csv(csv_path)
    missing = REQ_COLS - set(map(str, df.columns))
    if missing:
        raise SystemExit(
            f"CSV missing required columns: {sorted(missing)}\nGot: {list(df.columns)}"
        )

    if args.limit:
        df = df.head(args.limit)

    # Normalize basic types
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(1)
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date.astype(str)

    inserted = 0
    with connect(db_path) as con:
        for _, r in df.iterrows():
            item_id = get_or_create_item(con, r["item"], r.get("unit", "unit"))
            store_id = get_or_create_store(con, r.get("store"), r.get("city"))
            if pd.isna(r["price"]):
                continue
            con.execute(
                """INSERT INTO price(item_id, store_id, price, currency, quantity, date)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    item_id,
                    store_id,
                    float(r["price"]),
                    str(r.get("currency") or "USD"),
                    float(r.get("quantity") or 1),
                    str(r["date"]),
                ),
            )
            inserted += 1
        con.commit()

    print(f"✅ Imported {inserted} rows into {db_path} (item/store upsert + price insert)")


if __name__ == "__main__":
    main()
