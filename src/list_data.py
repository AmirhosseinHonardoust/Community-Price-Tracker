#!/usr/bin/env python3
from __future__ import annotations
from tabulate import tabulate
from db import connect, q

def main() -> None:
    with connect() as con:
        items = q(con, "SELECT * FROM item ORDER BY name")
        stores = q(con, "SELECT * FROM store ORDER BY name")
        prices = q(con, "SELECT p.id, i.name AS item, i.unit, s.name AS store, s.city, p.price, p.currency, p.quantity, p.date FROM price p LEFT JOIN item i ON i.id=p.item_id LEFT JOIN store s ON s.id=p.store_id ORDER BY p.date DESC, i.name")
    print("\nItems")
    print(tabulate(items, headers="keys", tablefmt="github"))
    print("\nStores")
    print(tabulate(stores, headers="keys", tablefmt="github"))
    print("\nPrices")
    print(tabulate(prices, headers="keys", tablefmt="github"))

if __name__ == "__main__":
    main()
