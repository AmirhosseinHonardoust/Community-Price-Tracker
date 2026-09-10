from pathlib import Path

from generate_data import DEFAULT_OUTFILE, generate


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
