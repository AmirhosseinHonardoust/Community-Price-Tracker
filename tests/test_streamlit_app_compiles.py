import py_compile
from pathlib import Path


def test_streamlit_app_compiles():
    """We can't run the Streamlit UI in CI without a browser/runtime, so this
    is a smoke test that the module at least parses and compiles cleanly."""
    path = Path(__file__).resolve().parents[1] / "src" / "streamlit_app.py"
    py_compile.compile(str(path), doraise=True)
