# Community Price Tracker

A **community-driven data app** for logging and analyzing the prices of everyday goods (milk, bread, eggs, fuel, etc.) over time.  
This project empowers local communities to **track inflation, compare cities, and visualize cost-of-living trends** using a fully local, privacy-friendly setup, built with **Python, SQLite, Pandas, and Streamlit**.

---

## Features

Log and manage:
- **Items**, **Stores**, and **Prices**
- Price, date, currency, and quantity  
- Multiple cities and stores  

Analyze and visualize:
- **Price trend charts** for any item  
- **Basket cost comparison** across cities  
- Data persistence via SQLite  
- Simple Streamlit UI for non-technical users  

---

## Tech Stack
| Component | Purpose |
|------------|----------|
| **Python 3.10+** | Core logic and data processing |
| **SQLite3** | Lightweight local database |
| **Pandas** | CSV and data analysis |
| **Matplotlib** | Chart generation |
| **Streamlit** | Interactive web interface |
| **CSV Generator** | Creates realistic price datasets |

---

## Project Structure
```
community-price-tracker/
│
├── data/
│   ├── prices.db               # SQLite database
│   ├── generated_prices.csv    # Synthetic dataset
│
├── outputs/
│   ├── trend_milk.png          # Sample trend chart
│   ├── basket_by_city.png      # Basket comparison chart
│
├── src/
│   ├── schema.sql              # Database schema
│   ├── db.py                   # SQLite helper functions
│   ├── init_db.py              # Initializes DB
│   ├── generate_data.py        # Generates synthetic CSV data
│   ├── import_csv.py           # Imports CSV → normalized schema
│   ├── analytics.py            # Generates charts
│   ├── streamlit_app.py        # Interactive web app
│   ├── add_item.py / add_store.py / add_price.py / list_data.py
│
└── README.md
```

---

## Installation & Setup

### Clone or download
```bash
git clone https://github.com/<your-username>/community-price-tracker.git
cd community-price-tracker
```

### Create a virtual environment
```bash
python -m venv .venv
.venv\Scripts\activate       # (Windows)
# source .venv/bin/activate    # (macOS/Linux)
```

### Install dependencies
```bash
pip install -r requirements.txt
```

### Initialize the database
```bash
python src/init_db.py
```

---

## Generate and Import Data

### Generate synthetic price data
```bash
python src/generate_data.py
```
This creates:
```
data/generated_prices.csv
```
containing 1000 random records for multiple items and cities.

### Import data into SQLite
```bash
python src/import_csv.py --file data/generated_prices.csv
```
Automatically:
- Creates new items and stores  
- Inserts prices with correct relations  

---

## Verify Your Data
List what’s inside the database:
```bash
python src/list_data.py
```
Expected output:
```
Items
| id | name   | unit  |
|----|--------|-------|
| 1  | Milk   | liter |
| 2  | Bread  | loaf  |

Stores
| id | name          | city     |
|----|---------------|----------|
| 1  | Market 1      | Helsinki |

Prices
| item | store | city     | price | date       |
|------|--------|----------|-------|------------|
| Milk | Market 1 | Helsinki | 1.35 | 2025-10-26 |
```

---

## Analytics & Charts

### Generate a price trend chart
```bash
python src/analytics.py --item Milk --outdir outputs
```
Creates:
```
outputs/trend_milk.png
```

### Compare basket cost across cities
```bash
python src/analytics.py --basket Milk Bread Eggs --outdir outputs
```
Creates:
```
outputs/basket_by_city.png
```

Example Output:

**Milk Price Trend**
<img width="960" height="720" alt="trend_milk" src="https://github.com/user-attachments/assets/b26df1d8-bf86-4250-b56b-66832e5b25d4" />

---

**Basket Cost by City**
<img width="960" height="720" alt="basket_by_city" src="https://github.com/user-attachments/assets/905133a1-6910-4224-b8e2-0d9de2b187ae" />

---

## Run the Streamlit App

```bash
streamlit run src/streamlit_app.py
```

### Web Features:
- Log new items, stores, and prices  
- View recent entries  
- Trend charts by item  
- Compare basket costs  
- 100% local and privacy-friendly  

---

## Database Schema

| Table | Columns |
|--------|----------|
| **item** | id, name, category, unit |
| **store** | id, name, city, latitude, longitude |
| **price** | id, item_id, store_id, price, currency, quantity, date |

> Indexed for faster queries on `(item_id, date)` and `(store_id, date)`.

---

## Example Use Case
Community volunteers across different cities can:
1. Log weekly prices for essential goods  
2. Visualize price inflation patterns  
3. Compare living costs between regions  
4. Share insights for economic awareness  

---

## Screenshot Gallery (Placeholders)

** Trends Tab**

<img width="657" height="558" alt="Screenshot 2025-10-27 at 10-47-32 Community Price Tracker" src="https://github.com/user-attachments/assets/c1c8cb78-adc3-4619-92e7-72ae614c30f2" />

---

** Basket Comparison**

<img width="684" height="616" alt="Screenshot 2025-10-27 at 10-46-38 Community Price Tracker" src="https://github.com/user-attachments/assets/77dd4c17-de07-4d8e-84e3-2b37d6e993d3" />

---

## Future Enhancements
- Export charts as PDF reports  
- Geolocation map view  
- Price change notifications  
- ML model for price forecasting  
