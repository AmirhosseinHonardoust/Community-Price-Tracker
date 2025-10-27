#!/usr/bin/env python3
from __future__ import annotations
import argparse
from pathlib import Path
import sys
import pandas as pd
import matplotlib.pyplot as plt
from db import connect, q

def ensure_outdir(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    return p

def _rows_to_df(rows) -> pd.DataFrame:
    """
    Convert sqlite rows to a DataFrame with proper column names.
    Handles cases where rows are sqlite3.Row or plain tuples.
    """
    if not rows:
        return pd.DataFrame()
    try:
        # sqlite3.Row is mapping-like: dict(row) works
        return pd.DataFrame([dict(r) for r in rows])
    except Exception:
        # Fallback: use cursor description — but we don't have cursor here.
        # So just coerce, and we’ll validate later.
        return pd.DataFrame(rows)

def load_prices_df() -> pd.DataFrame:
    with connect() as con:
        rows = q(con, """
            SELECT
              p.id,
              i.name AS item,
              i.unit,
              s.city,
              p.price,
              p.quantity,
              p.currency,
              p.date
            FROM price p
            LEFT JOIN item i ON i.id = p.item_id
            LEFT JOIN store s ON s.id = p.store_id
        """)
    df = _rows_to_df(rows)
    if df.empty:
        return df

    # Validate columns
    required = {"item", "unit", "city", "price", "quantity", "currency", "date"}
    missing = required - set(df.columns.astype(str))
    if missing:
        print("❌ Expected columns missing in query result:", sorted(missing))
        print("Columns I actually see:", list(df.columns))
        print("Tip: delete data/prices.db, re-run init_db.py, then add prices again.")
        sys.exit(1)

    # Safe conversions
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["unit_price"] = df["price"] / df["quantity"].replace(0, pd.NA)
    return df

def plot_trend(df: pd.DataFrame, item: str, outdir: Path) -> Path | None:
    dfi = df[df["item"].str.lower() == item.lower()].copy()
    if dfi.empty:
        return None
    dfi = dfi.sort_values("date")
    plt.figure()
    for city, grp in dfi.groupby(dfi["city"].fillna("Unknown")):
        plt.plot(grp["date"], grp["unit_price"], marker="o", label=city)
    plt.title(f"Price Trend: {item} (per unit)")
    plt.xlabel("Date")
    plt.ylabel("Unit Price")
    plt.legend()
    plt.grid(True, alpha=0.3)
    p = outdir / f"trend_{item.replace(' ','_').lower()}.png"
    plt.tight_layout()
    plt.savefig(p, dpi=150)
    plt.close()
    return p

def plot_basket(df: pd.DataFrame, items: list[str], outdir: Path) -> Path | None:
    dff = df[df["item"].str.lower().isin([x.lower() for x in items])].copy()
    if dff.empty:
        return None
    latest = dff.sort_values("date").groupby(["city", "item"]).tail(1)
    basket = latest.groupby("city")["unit_price"].sum().sort_values(ascending=False)
    plt.figure()
    basket.plot(kind="bar")
    plt.title("Basket Cost by City (sum of latest unit prices)")
    plt.xlabel("City")
    plt.ylabel("Total Cost")
    p = outdir / "basket_by_city.png"
    plt.tight_layout()
    plt.savefig(p, dpi=150)
    plt.close()
    return p

def main() -> None:
    ap = argparse.ArgumentParser(description="Generate charts from stored prices.")
    ap.add_argument("--item", action="append", help="Item name to plot trend (can repeat)")
    ap.add_argument("--basket", nargs="+", help="List of items to compare basket cost by city")
    ap.add_argument("--outdir", default=str(Path(__file__).resolve().parents[1] / "outputs"))
    args = ap.parse_args()

    out = ensure_outdir(Path(args.outdir))
    df = load_prices_df()
    if df.empty:
        print("No data available. Add prices first.")
        return

    if args.item:
        for it in args.item:
            p = plot_trend(df, it, out)
            print(f"Trend saved: {p}" if p else f"No data for item '{it}'")
    if args.basket:
        p = plot_basket(df, args.basket, out)
        print(f"Basket saved: {p}" if p else "No data for selected basket.")

if __name__ == "__main__":
    main()
