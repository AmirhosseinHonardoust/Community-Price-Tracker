from pathlib import Path

from db import connect, exec_script, q, qi
from list_data import _as_dicts

SCHEMA = Path(__file__).resolve().parents[1] / "src" / "schema.sql"


def test_as_dicts_produces_named_columns(tmp_path):
    """Regression test: tabulate(rows, headers='keys') needs dicts, not sqlite3.Row,
    or it silently falls back to positional 0/1/2 headers."""
    db_path = tmp_path / "t.db"
    with connect(db_path) as con:
        exec_script(con, SCHEMA)
        qi(con, "INSERT INTO item(name, unit) VALUES('Milk','liter')")
        rows = q(con, "SELECT id, name, unit FROM item")

    result = _as_dicts(rows)

    assert result == [{"id": 1, "name": "Milk", "unit": "liter"}]
    assert list(result[0].keys()) == ["id", "name", "unit"]
