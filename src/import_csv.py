#!/usr/bin/env python3
import argparse
import sqlite3
import pandas as pd
from pathlib import Path

REQ_COLS = {"item", "unit", "store", "city", "price", "currency", "quantity", "date"}

def get_or_create_item(con, name: str, unit: str) -> int:
    cur = con.execute("SELECT id FROM item WHERE name=?", (name.strip(),))
    row = cur.fetchone()
    if row:
        # Optional: update unit if empty in DB and provided in CSV
        con.execute("UPDATE item SET unit=COALESCE(NULLIF(unit,''), ?) WHERE id=?", (unit.strip(), row[0]))
        return row[0]
    cur = con.execute(
        "INSERT INTO item(name, category, unit) VALUES(?, 'general', ?)",
        (name.strip(), unit.strip() or "unit")
    )
    con.commit()
    return cur.lastrowid

def get_or_create_store(con, name: str | None, city: str | None) -> int | None:
    if not name or not name.strip():
        return None  # store is optional in schema
    cur = con.execute("SELECT id FROM store WHERE name=? AND COALESCE(city,'')=COALESCE(?, '')",
                      (name.strip(), (city or "").strip()))
    row = cur.fetchone()
    if row:
        return row[0]
    cur = con.execute(
        "INSERT INTO store(name, city) VALUES(?, ?)",
        (name.strip(), (city or "").strip() or None)
    )
    con.commit()
    return cur.lastrowid

def main():
    ap = argparse.ArgumentParser(description="Import denormalized CSV into normalized SQLite schema.")
    ap.add_argument("--db", default="data/prices.db", help="Path to SQLite DB")
    ap.add_argument("--file", required=True, help="CSV with columns: item,unit,store,city,price,currency,quantity,date")
    ap.add_argument("--limit", type=int, default=None, help="Import only first N rows (optional)")
    args = ap.parse_args()

    db_path = Path(args.db)
    csv_path = Path(args.file)
    if not db_path.exists():
        raise SystemExit(f"DB not found: {db_path}. Run: python src/init_db.py")
    if not csv_path.exists():
        raise SystemExit(f"CSV not found: {csv_path}")

    df = pd.read_csv(csv_path)
    missing = REQ_COLS - set(map(str, df.columns))
    if missing:
        raise SystemExit(f"CSV missing required columns: {sorted(missing)}\nGot: {list(df.columns)}")

    if args.limit:
        df = df.head(args.limit)

    # Normalize basic types
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(1)
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date.astype(str)

    inserted = 0
    with sqlite3.connect(db_path) as con:
        con.execute("PRAGMA foreign_keys = ON;")
        for _, r in df.iterrows():
            item_id = get_or_create_item(con, r["item"], r.get("unit", "unit"))
            store_id = get_or_create_store(con, r.get("store"), r.get("city"))
            if pd.isna(r["price"]):
                continue
            con.execute(
                """INSERT INTO price(item_id, store_id, price, currency, quantity, date)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (item_id,
                 store_id,
                 float(r["price"]),
                 str(r.get("currency") or "USD"),
                 float(r.get("quantity") or 1),
                 str(r["date"]))
            )
            inserted += 1
        con.commit()

    print(f"✅ Imported {inserted} rows into {db_path} (item/store upsert + price insert)")

if __name__ == "__main__":
    main()
