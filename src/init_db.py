#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
from db import connect, exec_script

def main() -> None:
    schema = Path(__file__).resolve().parent / "schema.sql"
    with connect() as con:
        exec_script(con, schema)
    print("Database initialized ✅")

if __name__ == "__main__":
    main()
