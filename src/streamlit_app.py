#!/usr/bin/env python3
"""Streamlit UI: log price observations and view trend/basket charts."""

from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st

from dataframe_utils import require_columns, rows_to_df, with_unit_price
from db import connect, get_or_create_item, get_or_create_store, price_rows, q, qi

st.set_page_config(page_title="Community Price Tracker", page_icon="🧾", layout="centered")
st.title("🧾 Community Price Tracker")


def assert_columns(df: pd.DataFrame, required: set[str], context: str) -> None:
    """Stop the page with a friendly error if `df` is missing required columns."""
    try:
        require_columns(df, required, context)
    except ValueError as exc:
        st.error(f"❌ {exc}")
        st.stop()


tab1, tab2, tab3, tab4 = st.tabs(["Log Price", "Items & Stores", "Trends", "Basket"])

with tab1:
    st.subheader("Log a Price Observation")
    with connect() as con:
        items = q(con, "SELECT id, name, unit FROM item ORDER BY name")
        stores = q(con, "SELECT id, name, city FROM store ORDER BY name")
    col1, col2 = st.columns(2)
    new_item = col1.text_input("New item name (optional)", key="new_item")
    item_options = {f"{x['name']} ({x['unit']})": x["id"] for x in items}
    item_select = col2.selectbox(
        "Existing item", ["-- Select --"] + list(item_options.keys()), key="item_select"
    )
    price = st.number_input("Price", min_value=0.0, step=0.1, key="price")
    currency = st.text_input("Currency", value="USD", key="currency")
    quantity = st.number_input(
        "Quantity (in item units)", min_value=0.1, value=1.0, step=0.1, key="quantity"
    )
    d = st.date_input("Date", value=date.today(), key="log_date")

    st.markdown("**Store**")
    col3, col4 = st.columns(2)
    new_store = col3.text_input("New store name (optional)", key="new_store")
    new_city = col4.text_input("City (optional)", key="new_city")
    store_options = {"-- None --": None}
    store_options.update({f"{x['name']} ({x['city'] or 'unknown'})": x["id"] for x in stores})
    store_select = st.selectbox("Existing store", list(store_options.keys()), key="store_select")

    if st.button("Save price", key="save_price_btn"):
        with connect() as con:
            if new_item.strip():
                # BUG FIX: this used to INSERT OR IGNORE + re-select by name,
                # duplicating get_or_create_item's logic without its unit
                # backfill. Reusing the shared helper keeps this in sync with
                # the CLI (add_item.py) instead of drifting.
                item_id = get_or_create_item(con, new_item.strip())
            else:
                if item_select == "-- Select --":
                    st.error("Choose an existing item or enter a new one.")
                    st.stop()
                item_id = item_options[item_select]

            if new_store.strip():
                # BUG FIX: this used to always INSERT a new store row, so
                # logging a price for the same new store name+city twice (e.g.
                # two form submits) created duplicate store rows and split
                # that store's price history across two ids. add_store.py was
                # fixed for this same issue previously; reusing
                # get_or_create_store here keeps both entry points consistent.
                store_id = get_or_create_store(con, new_store.strip(), new_city.strip())
            else:
                store_id = store_options[store_select]

            qi(
                con,
                "INSERT INTO price(item_id, store_id, price, currency, quantity, date) "
                "VALUES(?,?,?,?,?,?)",
                (item_id, store_id, float(price), currency.strip(), float(quantity), d.isoformat()),
            )
        st.success("Price logged ✅")

with tab2:
    st.subheader("Items, Stores & Recent Prices")
    with connect() as con:
        items_df = rows_to_df(q(con, "SELECT * FROM item ORDER BY name"))
        stores_df = rows_to_df(q(con, "SELECT * FROM store ORDER BY name"))
        prices_df = rows_to_df(price_rows(con, limit=500))
    st.write("**Items**")
    st.dataframe(items_df)
    st.write("**Stores**")
    st.dataframe(stores_df)
    st.write("**Recent Prices**")
    if not prices_df.empty:
        assert_columns(
            prices_df,
            {"item", "unit", "store", "city", "price", "currency", "quantity", "date"},
            "Recent Prices",
        )
    st.dataframe(prices_df)

with tab3:
    st.subheader("Trends")
    item_name = st.text_input("Item name to visualize (exact)", value="Milk", key="trend_item")
    if st.button("Show trend", key="show_trend_btn"):
        with connect() as con:
            rows = price_rows(con, item_names=[item_name.strip()]) if item_name.strip() else []
        trend_df = rows_to_df(rows)
        if trend_df.empty:
            st.warning("No data for that item yet.")
        else:
            assert_columns(
                trend_df, {"item", "unit", "city", "price", "quantity", "date"}, "Trends query"
            )
            trend_df["date"] = pd.to_datetime(trend_df["date"], errors="coerce")
            trend_df = with_unit_price(trend_df)
            pivot = trend_df.pivot_table(
                index="date", columns="city", values="unit_price", aggfunc="mean"
            ).sort_index()
            st.line_chart(pivot)

with tab4:
    st.subheader("Basket Cost by City")
    basket = st.text_input(
        "Items (comma-separated)", value="Milk,Bread,Eggs", key="basket_items_input"
    )
    if st.button("Compare basket", key="compare_basket_btn"):
        basket_items = [x.strip() for x in basket.split(",") if x.strip()]
        if not basket_items:
            st.warning("Enter at least one item.")
        else:
            with connect() as con:
                rows = price_rows(con, item_names=basket_items)
            basket_df = rows_to_df(rows)
            if basket_df.empty:
                st.warning("No data for these items yet.")
            else:
                assert_columns(
                    basket_df, {"item", "city", "price", "quantity", "date"}, "Basket query"
                )
                latest = (
                    with_unit_price(
                        basket_df.assign(date=pd.to_datetime(basket_df["date"], errors="coerce"))
                    )
                    .sort_values("date")
                    .groupby(["city", "item"])
                    .tail(1)
                )
                basket_cost = (
                    latest.groupby("city")["unit_price"].sum().sort_values(ascending=False)
                )
                st.bar_chart(basket_cost)

st.caption("Built with SQLite + Streamlit • Store local, share insights global 🌍")
