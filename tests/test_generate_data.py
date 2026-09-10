import csv
from datetime import date, timedelta
from pathlib import Path

from generate_data import DEFAULT_OUTFILE, LOOKBACK_DAYS, generate


def test_generate_writes_to_explicit_path(tmp_path):
    out = generate(tmp_path / "custom.csv", count=5)
    assert out == tmp_path / "custom.csv"
    lines = out.read_text().strip().splitlines()
    assert len(lines) == 6  # header + 5 rows


def test_default_outfile_is_repo_root_data_dir():
    """Regression test: the default path must resolve relative to this file's
    location (repo_root/data), not the process's current working directory."""
    repo_root = Path(__file__).resolve().parents[1]
    assert repo_root / "data" / "generated_prices.csv" == DEFAULT_OUTFILE


def test_generated_dates_fall_within_lookback_window_of_end_date(tmp_path):
    """Regression test: dates must be relative to `end_date` (defaults to
    today), not a hardcoded past window that goes stale over time."""
    end = date(2030, 6, 15)
    start = end - timedelta(days=LOOKBACK_DAYS)
    out = generate(tmp_path / "dated.csv", count=50, end_date=end)
    with out.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    dates = [date.fromisoformat(r["date"]) for r in rows]
    assert all(start <= d <= end for d in dates)
