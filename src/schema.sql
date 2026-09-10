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

-- Defense in depth: get_or_create_store() in db.py already dedupes stores by
-- (name, COALESCE(city,'')) at the app level, but nothing previously stopped
-- a duplicate row if that helper were bypassed (this is exactly how the
-- streamlit_app.py "new store" bug produced duplicate stores before it was
-- fixed to call get_or_create_store()). This mirrors that same lookup
-- expression so any duplicate insert now fails loudly instead of silently
-- fragmenting a store's price history across two ids.
CREATE UNIQUE INDEX IF NOT EXISTS idx_store_name_city ON store(name, COALESCE(city, ''));
