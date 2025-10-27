#!/usr/bin/env python3
from __future__ import annotations
from datetime import date
import sys
import pandas as pd
import streamlit as st
from db import connect, q, qi

st.set_page_config(page_title="Community Price Tracker", page_icon="🧾", layout="centered")
st.title("🧾 Community Price Tracker")

# -------- helpers --------
def rows_to_df(rows) -> pd.DataFrame:
    """Always return a DataFrame with named columns."""
    if not rows:
        return pd.DataFrame()
    try:
        return pd.DataFrame([dict(r) for r in rows])  # sqlite3.Row -> dict
    except Exception:
        return pd.DataFrame(rows)  # fallback (no names)

def assert_columns(df: pd.DataFrame, required: set[str], context: str) -> None:
    missing = required - set(map(str, df.columns))
    if missing:
        st.error(
            f"❌ Missing expected columns in {context}: {sorted(missing)}\n\n"
            f"Seen columns: {list(df.columns)}\n\n"
            "Fix: delete `data/prices.db`, run `python src/init_db.py`, "
            "then add prices again with `src/add_price.py`."
        )
        st.stop()

tab1, tab2, tab3, tab4 = st.tabs(["Log Price", "Items & Stores", "Trends", "Basket"])

with tab1:
    st.subheader("Log a Price Observation")
    with connect() as con:
        items = q(con, "SELECT id, name, unit FROM item ORDER BY name")
        stores = q(con, "SELECT id, name, city FROM store ORDER BY name")
    col1, col2 = st.columns(2)
    new_item = col1.text_input("New item name (optional)")
    item_options = {f"{x['name']} ({x['unit']})": x["id"] for x in items}
    item_select = col2.selectbox("Existing item", ["-- Select --"] + list(item_options.keys()))
    price = st.number_input("Price", min_value=0.0, step=0.1)
    currency = st.text_input("Currency", value="USD")
    quantity = st.number_input("Quantity (in item units)", min_value=0.1, value=1.0, step=0.1)
    d = st.date_input("Date", value=date.today())

    st.markdown("**Store**")
    col3, col4 = st.columns(2)
    new_store = col3.text_input("New store name (optional)")
    new_city = col4.text_input("City (optional)")
    store_options = {"-- None --": None}
    store_options.update({f"{x['name']} ({x['city'] or 'unknown'})": x["id"] for x in stores})
    store_select = st.selectbox("Existing store", list(store_options.keys()))

    if st.button("Save price"):
        with connect() as con:
            if new_item.strip():
                qi(con, "INSERT OR IGNORE INTO item(name, category, unit) VALUES(?, 'general', 'unit')", (new_item.strip(),))
                item_id = q(con, "SELECT id FROM item WHERE name=? ORDER BY id DESC", (new_item.strip(),))[0]["id"]
            else:
                if item_select == "-- Select --":
                    st.error("Choose an existing item or enter a new one.")
                    st.stop()
                item_id = item_options[item_select]

            if new_store.strip():
                qi(con, "INSERT INTO store(name, city) VALUES(?,?)", (new_store.strip(), new_city.strip() or None))
                store_id = q(con, "SELECT id FROM store WHERE name=? ORDER BY id DESC", (new_store.strip(),))[0]["id"]
            else:
                store_id = store_options[store_select]

            qi(con, "INSERT INTO price(item_id, store_id, price, currency, quantity, date) VALUES(?,?,?,?,?,?)",
               (item_id, store_id, float(price), currency.strip(), float(quantity), d.isoformat()))
        st.success("Price logged ✅")

with tab2:
    st.subheader("Items, Stores & Recent Prices")
    with connect() as con:
        items = rows_to_df(q(con, "SELECT * FROM item ORDER BY name"))
        stores = rows_to_df(q(con, "SELECT * FROM store ORDER BY name"))
        prices = rows_to_df(q(con, """
            SELECT
              p.id,
              i.name  AS item,
              i.unit  AS unit,
              s.name  AS store,
              s.city  AS city,
              p.price AS price,
              p.currency AS currency,
              p.quantity AS quantity,
              p.date AS date
            FROM price p
            LEFT JOIN item  i ON i.id = p.item_id
            LEFT JOIN store s ON s.id = p.store_id
            ORDER BY p.date DESC
            LIMIT 500
        """))
    st.write("**Items**")
    st.dataframe(items)
    st.write("**Stores**")
    st.dataframe(stores)
    st.write("**Recent Prices**")
    if not prices.empty:
        assert_columns(prices, {"item","unit","store","city","price","currency","quantity","date"}, "Recent Prices")
    st.dataframe(prices)

with tab3:
    st.subheader("Trends")
    item_name = st.text_input("Item name to visualize (exact)", value="Milk")
    if st.button("Show trend"):
        with connect() as con:
            rows = q(con, """
                SELECT
                  i.name AS item,
                  i.unit AS unit,
                  s.city AS city,
                  p.price AS price,
                  p.quantity AS quantity,
                  p.date AS date
                FROM price p
                LEFT JOIN item  i ON i.id = p.item_id
                LEFT JOIN store s ON s.id = p.store_id
                WHERE lower(i.name) = lower(?)
            """, (item_name.strip(),))
        df = rows_to_df(rows)
        if df.empty:
            st.warning("No data for that item yet.")
        else:
            assert_columns(df, {"item","unit","city","price","quantity","date"}, "Trends query")
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
            df["unit_price"] = df["price"] / df["quantity"].replace(0, pd.NA)
            pivot = (df.pivot_table(index="date", columns="city", values="unit_price", aggfunc="mean")
                       .sort_index())
            st.line_chart(pivot)

with tab4:
    st.subheader("Basket Cost by City")
    basket = st.text_input("Items (comma-separated)", value="Milk,Bread,Eggs")
    if st.button("Compare basket"):
        items = [x.strip() for x in basket.split(",") if x.strip()]
        if not items:
            st.warning("Enter at least one item.")
        else:
            qmarks = ",".join("?" * len(items))
            sql = f"""
                SELECT
                  i.name AS item,
                  s.city AS city,
                  p.price AS price,
                  p.quantity AS quantity,
                  p.date AS date
                FROM price p
                LEFT JOIN item  i ON i.id = p.item_id
                LEFT JOIN store s ON s.id = p.store_id
                WHERE lower(i.name) IN ({qmarks})
            """
            with connect() as con:
                rows = q(con, sql, tuple(map(str.lower, items)))
            df = rows_to_df(rows)
            if df.empty:
                st.warning("No data for these items yet.")
            else:
                assert_columns(df, {"item","city","price","quantity","date"}, "Basket query")
                latest = (df.assign(date=pd.to_datetime(df["date"], errors="coerce"))
                            .sort_values("date")
                            .assign(unit_price=lambda d: d["price"]/d["quantity"].replace(0, pd.NA))
                            .groupby(["city","item"]).tail(1))
                basket_cost = latest.groupby("city")["unit_price"].sum().sort_values(ascending=False)
                st.bar_chart(basket_cost)

st.caption("Built with SQLite + Streamlit • Store local, share insights global 🌍")
