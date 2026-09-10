#!/usr/bin/env python3
"""Generate a synthetic CSV of price observations for demos and testing."""

from __future__ import annotations

import csv
import random
from datetime import date, timedelta
from pathlib import Path

ITEMS = [
    ("Milk", "liter"),
    ("Bread", "loaf"),
    ("Eggs", "dozen"),
    ("Rice", "kg"),
    ("Apples", "kg"),
    ("Sugar", "kg"),
    ("Coffee", "pack"),
    ("Butter", "pack"),
]
CITIES = ["Helsinki", "Berlin", "Paris", "Madrid", "Warsaw", "Rome", "Lisbon"]
STORES = [f"Market {i}" for i in range(1, 8)]
BASE_PRICES = {
    "Milk": 1.3,
    "Bread": 1.2,
    "Eggs": 2.0,
    "Rice": 3.0,
    "Apples": 2.5,
    "Sugar": 2.2,
    "Coffee": 4.5,
    "Butter": 2.8,
}
DEFAULT_COUNT = 1000

# Resolved relative to this file, not the current working directory, so the
# output always lands in <repo_root>/data regardless of where the script is
# invoked from (e.g. running `python generate_data.py` from inside src/).
DEFAULT_OUTFILE = Path(__file__).resolve().parents[1] / "data" / "generated_prices.csv"


def generate(outfile: Path | None = None, count: int = DEFAULT_COUNT) -> Path:
    """Generate `count` synthetic price rows and write them to `outfile` as CSV.

    Returns the path written to. Defaults to DEFAULT_OUTFILE.
    """
    out = outfile or DEFAULT_OUTFILE
    out.parent.mkdir(parents=True, exist_ok=True)

    start_date = date(2025, 1, 1)
    end_date = date(2025, 10, 25)
    days = (end_date - start_date).days

    rows = []
    for _ in range(count):
        item, unit = random.choice(ITEMS)
        city = random.choice(CITIES)
        store = random.choice(STORES)
        d = start_date + timedelta(days=random.randint(0, days))
        price = round(BASE_PRICES[item] * random.uniform(0.9, 1.3), 2)
        rows.append([item, unit, store, city, price, "EUR", 1, d.isoformat()])

    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["item", "unit", "store", "city", "price", "currency", "quantity", "date"])
        w.writerows(rows)

    return out


def main() -> None:
    out = generate()
    print(f"✅ Generated {DEFAULT_COUNT} price rows -> {out}")


if __name__ == "__main__":
    main()
