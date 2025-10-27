-- Community Price Tracker schema (SQLite)
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS item (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE,
  category TEXT,
  unit TEXT NOT NULL DEFAULT 'unit'
);

CREATE TABLE IF NOT EXISTS store (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  city TEXT,
  latitude REAL,
  longitude REAL
);

CREATE TABLE IF NOT EXISTS price (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  item_id INTEGER NOT NULL REFERENCES item(id) ON DELETE CASCADE,
  store_id INTEGER REFERENCES store(id) ON DELETE SET NULL,
  price REAL NOT NULL CHECK(price >= 0),
  currency TEXT NOT NULL DEFAULT 'USD',
  quantity REAL NOT NULL DEFAULT 1,
  date TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_price_item_date ON price(item_id, date);
CREATE INDEX IF NOT EXISTS idx_price_store_date ON price(store_id, date);
