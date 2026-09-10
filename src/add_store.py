#!/usr/bin/env python3
"""CLI to add a store / market. Idempotent by (name, city) -- see BEHAVIOR CHANGE below."""

from __future__ import annotations

import argparse

from db import add_db_arg, connect, get_or_create_store, resolve_db_path


def main() -> None:
    ap = argparse.ArgumentParser(description="Add a store / market (idempotent by name+city).")
    ap.add_argument("--name", required=True)
    ap.add_argument("--city", default="")
    ap.add_argument("--lat", type=float, default=None)
    ap.add_argument("--lon", type=float, default=None)
    add_db_arg(ap)
    args = ap.parse_args()

    # BUG FIX: a blank --name used to sail through argparse's required=True
    # check, then silently return None from get_or_create_store (its
    # "no store given" sentinel) with no error -- so `add_store.py --name " "`
    # printed "Store ready with id=None" instead of failing loudly.
    if not args.name.strip():
        raise SystemExit("--name must not be blank")

    with connect(resolve_db_path(args.db)) as con:
        # BEHAVIOR CHANGE: previously this always inserted a new row, so running
        # this command twice with the same name/city silently created duplicate
        # stores. It now reuses the existing store, matching import_csv.py's
        # get_or_create_store semantics.
        store_id = get_or_create_store(con, args.name, args.city)
        if args.lat is not None or args.lon is not None:
            con.execute(
                "UPDATE store SET latitude=?, longitude=? WHERE id=?",
                (args.lat, args.lon, store_id),
            )
            con.commit()
    print(f"Store ready with id={store_id} ✅")


if __name__ == "__main__":
    main()
