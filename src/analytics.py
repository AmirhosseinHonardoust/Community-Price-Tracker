#!/usr/bin/env python3
"""Generate price-trend and basket-cost charts from the SQLite database."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from dataframe_utils import require_columns, rows_to_df, with_unit_price
from db import connect, price_rows


def ensure_outdir(p: Path) -> Path:
    """Create `p` (and parents) if needed and return it."""
    p.mkdir(parents=True, exist_ok=True)
    return p


def load_prices_df() -> pd.DataFrame:
    """Load all price observations joined with item/store info, with unit_price computed."""
    with connect() as con:
        rows = price_rows(con)
    df = rows_to_df(rows)
    if df.empty:
        return df

    try:
        require_columns(
            df, {"item", "unit", "city", "price", "quantity", "currency", "date"}, "price query"
        )
    except ValueError as exc:
        print(f"❌ {exc}")
        sys.exit(1)

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = with_unit_price(df)
    return df


def plot_trend(df: pd.DataFrame, item: str, outdir: Path) -> Path | None:
    """Plot unit-price trend for `item` by city; returns the saved PNG path, or None."""
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
    p = outdir / f"trend_{item.replace(' ', '_').lower()}.png"
    plt.tight_layout()
    plt.savefig(p, dpi=150)
    plt.close()
    return p


def plot_basket(df: pd.DataFrame, items: list[str], outdir: Path) -> Path | None:
    """Plot summed latest unit price of `items` by city; returns the saved PNG path, or None."""
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
