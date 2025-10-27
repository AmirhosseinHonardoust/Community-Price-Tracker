#!/usr/bin/env python3
import csv, random
from datetime import date, timedelta
from pathlib import Path

items = [
    ("Milk", "liter"),
    ("Bread", "loaf"),
    ("Eggs", "dozen"),
    ("Rice", "kg"),
    ("Apples", "kg"),
    ("Sugar", "kg"),
    ("Coffee", "pack"),
    ("Butter", "pack")
]

cities = ["Helsinki", "Berlin", "Paris", "Madrid", "Warsaw", "Rome", "Lisbon"]
stores = [f"Market {i}" for i in range(1, 8)]

start_date = date(2025, 1, 1)
end_date = date(2025, 10, 25)
days = (end_date - start_date).days

out = Path("data/generated_prices.csv")
out.parent.mkdir(exist_ok=True)

rows = []
for _ in range(1000):
    item, unit = random.choice(items)
    city = random.choice(cities)
    store = random.choice(stores)
    d = start_date + timedelta(days=random.randint(0, days))
    base = {"Milk": 1.3, "Bread": 1.2, "Eggs": 2.0, "Rice": 3.0,
            "Apples": 2.5, "Sugar": 2.2, "Coffee": 4.5, "Butter": 2.8}[item]
    price = round(base * random.uniform(0.9, 1.3), 2)
    rows.append([item, unit, store, city, price, "EUR", 1, d.isoformat()])

with out.open("w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["item","unit","store","city","price","currency","quantity","date"])
    w.writerows(rows)

print(f"✅ Generated {len(rows)} price rows -> {out}")
