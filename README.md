<div align="center">

# Community Price Tracker

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![SQLite](https://img.shields.io/badge/SQLite-Local%20Storage-orange)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-green)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red)
![Status](https://img.shields.io/badge/Status-Community%20Project-purple)
[![CI](https://github.com/AmirhosseinHonardoust/Community-Price-Tracker/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/AmirhosseinHonardoust/Community-Price-Tracker/actions/workflows/ci.yml)

</div>

A **community-driven data app** that turns everyday price observations into **local price and inflation insight**, using a **SQLite-backed Pandas pipeline** with **synthetic data generation**, **CSV import**, **trend and basket analytics**, and a **Streamlit dashboard**.

> **Important:** This project is a **community data-logging and visualization tool**, not an official statistics source.
>
> The charts and comparisons reflect whatever prices your community logs. They are only as accurate and representative as the data entered, and should not be used as a substitute for official inflation or cost-of-living statistics.

---

## Table of Contents

- [Project Overview](#project-overview)
- [What This Project Does](#what-this-project-does)
- [What This Project Does Not Do](#what-this-project-does-not-do)
- [Key Features](#key-features)
- [System Workflow](#system-workflow)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Generating and Importing Data](#generating-and-importing-data)
- [Verifying Your Data](#verifying-your-data)
- [Analytics and Charts](#analytics-and-charts)
- [Streamlit Dashboard](#streamlit-dashboard)
- [Database Schema](#database-schema)
- [Visual Reports](#visual-reports)
- [Testing and CI](#testing-and-ci)
- [Code Quality](#code-quality)
- [Limitations](#limitations)
- [Responsible Use](#responsible-use)
- [Future Improvements](#future-improvements)
- [Tech Stack](#tech-stack)
- [Author](#author)
- [License](#license)

---

## Project Overview

Local price data is often scattered across memory, receipts, and word of mouth, with no easy way to see how prices are actually moving where you live. A price log is only useful if it can support a defensible comparison:

- log real observed prices for everyday goods, by store and city
- track how an item's price moves over time
- compare the cost of a basket of goods across cities
- keep the data local and private rather than sending it to a third party

This project demonstrates an end-to-end, local-first data workflow for community price tracking. It includes a normalized SQLite schema, synthetic data generation for demos, CSV import, price-trend and basket-comparison analytics, and a Streamlit dashboard.

The goal is to show how a small group of contributors can turn scattered price observations into a **shared, privacy-friendly view of local cost-of-living trends**, not just a spreadsheet of numbers.

---

## What This Project Does

This project can:

- Log **Items**, **Stores**, and **Prices**, including date, currency, and quantity
- Track multiple cities and stores in a single local database
- Generate a synthetic price dataset for demos and testing
- Import price data in bulk from CSV into the normalized schema
- List and filter logged data by item, city, or store
- Delete a mis-entered price by id
- Generate a **price trend chart** for any item
- Generate a **basket cost comparison** chart across cities
- Provide a Streamlit dashboard for non-technical users
- Run automated tests and CI checks on every push

---

## What This Project Does Not Do

This project does **not**:

- Guarantee statistically representative or official price data
- Fetch prices automatically from stores, receipts, or the web
- Replace government inflation or cost-of-living statistics
- Verify that a logged price was entered correctly
- Share or upload logged data anywhere by default
- Make purchasing, investment, or policy decisions on your behalf

A production-grade cost-of-living tool would need verified data sources, a much larger contributor base, and statistical weighting by region.

---

## Key Features

- **Normalized SQLite schema** for items, stores, and prices
- **Synthetic data generator** for realistic demo datasets
- **CSV import pipeline** that maps rows to items, stores, and prices automatically
- **Shared `price_rows()` query helper** so every script reads data the same way
- **Configurable database path** via `--db` flag or `CPT_DB_PATH` environment variable
- **Price trend charts** for any tracked item
- **Basket cost comparison** across cities
- **Streamlit dashboard** for interactive, non-technical use
- **Command-line tools** for adding, listing, and deleting records
- **Unit tests and GitHub Actions CI**
- **100% local, privacy-friendly** — nothing leaves your machine

---

## System Workflow

```text
Raw price observation (item, store, city, price, date)
        ↓
CSV import or manual entry (add_item / add_store / add_price)
        ↓
Normalized SQLite schema (item, store, price)
        ↓
Shared price_rows() query helper
        ↓
Pandas analysis (trend, basket comparison)
        ↓
Matplotlib charts
        ↓
Streamlit dashboard and command-line review
```

---

## Project Structure

```text
Community-Price-Tracker/
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── data/
│   ├── prices.db
│   └── generated_prices.csv
│
├── outputs/
│   ├── trend_milk.png
│   └── basket_by_city.png
│
├── src/
│   ├── schema.sql
│   ├── db.py
│   ├── dataframe_utils.py
│   ├── init_db.py
│   ├── generate_data.py
│   ├── import_csv.py
│   ├── analytics.py
│   ├── streamlit_app.py
│   ├── add_item.py
│   ├── add_store.py
│   ├── add_price.py
│   ├── list_data.py
│   └── delete_price.py
│
├── tests/
│
├── README.md
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
└── requirements.lock
```

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/AmirhosseinHonardoust/Community-Price-Tracker.git
cd Community-Price-Tracker
```

### 2. Create a Virtual Environment

On Windows CMD:

```cmd
python -m venv .venv
.venv\Scripts\activate
```

On macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Requirements

```bash
pip install -r requirements.txt
```

For development tools (pytest, Ruff, Black, mypy):

```bash
pip install -r requirements-dev.txt
```

---

## Quick Start

Initialize the database:

```bash
python src/init_db.py
```

Launch the dashboard:

```bash
streamlit run src/streamlit_app.py
```

List logged data from the command line:

```bash
python src/list_data.py
```

---

## Configuration

By default, every script reads and writes `data/prices.db` relative to the repository root. Override this with the `CPT_DB_PATH` environment variable, or pass `--db <path>` to any individual command:

```bash
export CPT_DB_PATH=/path/to/another.db   # Windows: set CPT_DB_PATH=...
python src/init_db.py
python src/list_data.py
```

`--db` always wins if given; otherwise `CPT_DB_PATH` is used; otherwise it falls back to `data/prices.db`. This precedence is consistent across every script (`add_item.py`, `add_store.py`, `add_price.py`, `import_csv.py`, `list_data.py`).

---

## Generating and Importing Data

Generate a synthetic price dataset:

```bash
python src/generate_data.py
```

This creates:

```text
data/generated_prices.csv
```

containing 1,000 random records across multiple items and cities.

Import the data into SQLite:

```bash
python src/import_csv.py --file data/generated_prices.csv
```

Import automatically:

- creates new items and stores as needed
- inserts prices with the correct relations

---

## Verifying Your Data

List what's inside the database:

```bash
python src/list_data.py
```

Optionally filter the Prices table:

```bash
python src/list_data.py --item Milk --city Helsinki --limit 20
```

Delete a mis-entered price by id (find the id from `list_data.py` output):

```bash
python src/delete_price.py --id 42
```

---

## Analytics and Charts

Generate a price trend chart:

```bash
python src/analytics.py --item Milk --outdir outputs
```

Generated output:

```text
outputs/trend_milk.png
```

Compare basket cost across cities:

```bash
python src/analytics.py --basket Milk Bread Eggs --outdir outputs
```

Generated output:

```text
outputs/basket_by_city.png
```

---

## Streamlit Dashboard

Launch the app:

```bash
streamlit run src/streamlit_app.py
```

The dashboard helps you:

- log new items, stores, and prices
- review recently logged entries
- view trend charts by item
- compare basket costs across cities
- work entirely locally, with no data leaving your machine

<div align="center">
<img width="676" alt="Streamlit dashboard" src="https://github.com/user-attachments/assets/c1c8cb78-adc3-4619-92e7-72ae614c30f2" />
</div>

---

## Database Schema

<div align="center">

| Table | Columns |
|---|---|
| `item` | id, name, category, unit |
| `store` | id, name, city, latitude, longitude |
| `price` | id, item_id, store_id, price, currency, quantity, date |

</div>

> Indexed for faster queries on `(item_id, date)` and `(store_id, date)`.

---

## Visual Reports

### Price trend and basket comparison

<div align="center">

| Milk Price Trend | Basket Cost by City |
|---|---|
| ![Milk price trend](https://github.com/user-attachments/assets/b26df1d8-bf86-4250-b56b-66832e5b25d4) | ![Basket cost by city](https://github.com/user-attachments/assets/905133a1-6910-4224-b8e2-0d9de2b187ae) |
| **Analysis:** The trend chart shows how one item's logged price moves over time, which is the simplest signal of local inflation. | **Analysis:** The basket chart shows relative cost-of-living differences across cities based on the same set of goods. |

</div>

<details>
<summary>Additional dashboard screenshots</summary>

<div align="center">

![Trends tab screenshot](https://github.com/user-attachments/assets/c1c8cb78-adc3-4619-92e7-72ae614c30f2)

![Basket comparison screenshot](https://github.com/user-attachments/assets/77dd4c17-de07-4d8e-84e3-2b37d6e993d3)

The Streamlit dashboard's Trends tab and Basket Comparison tab mirror the same charts interactively, with filters for item, city, and date range.

</div>

</details>

---

## Testing and CI

Run unit tests locally:

```bash
pytest -q --cov=src --cov-report=term-missing --cov-fail-under=85
```

Lint, format-check, and type-check:

```bash
ruff check --select E,F,I,B,SIM,UP --line-length 100 src tests
black --check --line-length 100 src tests
mypy --ignore-missing-imports src
```

The GitHub Actions workflow checks:

- dependency installation
- linting with Ruff
- formatting with Black
- type-checking with mypy
- unit tests with coverage

CI is defined in:

```text
.github/workflows/ci.yml
```

`requirements.lock` pins exact, known-good versions (generated for Python 3.11, matching CI) for a reproducible local install — CI itself installs from the loose ranges in `requirements.txt`.

---

## Code Quality

The project separates responsibilities across modules:

<div align="center">

| Module | Purpose |
|---|---|
| `src/schema.sql` | Database schema definition |
| `src/db.py` | SQLite helpers and the shared `price_rows()` query |
| `src/dataframe_utils.py` | Shared DataFrame helpers (unit price, column checks) |
| `src/init_db.py` | Initializes the database |
| `src/generate_data.py` | Generates synthetic CSV data |
| `src/import_csv.py` | Imports CSV data into the normalized schema |
| `src/analytics.py` | Generates trend and basket charts |
| `src/streamlit_app.py` | Interactive dashboard |

</div>

Tooling is configured through `pyproject.toml` (Ruff, Black, mypy, pytest) and `requirements-dev.txt`.

---

## Limitations

This project has important limitations:

- Logged prices are only as accurate as whoever enters them
- The dataset can be entirely synthetic unless a community actively imports real data
- Small or single-contributor datasets are not statistically representative
- The schema does not currently deduplicate near-identical entries
- Trend and basket charts reflect logged data only, not a full market basket
- The app does not verify prices against receipts or external sources

The project is strongest as a demonstration of a local-first, privacy-friendly data workflow, not as an authoritative pricing source.

---

## Responsible Use

This repository is intended for:

- community data logging and local analytics education
- demonstrating a local-first, privacy-friendly app design
- practicing SQLite, Pandas, and Streamlit workflows
- exploring price-trend and basket-comparison analysis
- portfolio demonstration

It should not be used as-is for:

- official inflation or cost-of-living reporting
- financial or investment decisions
- large-scale or commercial price aggregation
- any decision requiring verified, audited data

A production deployment would require verified data sources, a much larger and diverse contributor base, and statistical review.

---

## Future Improvements

Potential next improvements:

- Export charts as PDF reports
- Add a geolocation map view of stores and prices
- Add price-change notifications
- Add an ML model for price forecasting
- Add deduplication for near-identical entries
- Add multi-user sync while preserving local-first privacy

---

## Tech Stack

- Python
- SQLite3
- pandas
- Matplotlib
- Streamlit
- pytest
- Ruff
- Black
- mypy
- GitHub Actions

---

## Author

**Amir Honardoust**

GitHub: [@AmirhosseinHonardoust](https://github.com/AmirhosseinHonardoust)

---

## License

This project is intended for educational, community, and portfolio purposes.

If you use or modify this project, please keep the responsible-use notes and limitations clear.
