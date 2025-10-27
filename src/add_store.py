#!/usr/bin/env python3
from __future__ import annotations
import argparse
from db import connect, qi

def main() -> None:
    ap = argparse.ArgumentParser(description="Add a store / market.")
    ap.add_argument("--name", required=True)
    ap.add_argument("--city", default="")
    ap.add_argument("--lat", type=float, default=None)
    ap.add_argument("--lon", type=float, default=None)
    args = ap.parse_args()

    with connect() as con:
        rowid = qi(con, "INSERT INTO store(name, city, latitude, longitude) VALUES(?,?,?,?)",
                   (args.name.strip(), args.city.strip(), args.lat, args.lon)).lastrowid
    print(f"Store added with id={rowid} ✅")

if __name__ == "__main__":
    main()
