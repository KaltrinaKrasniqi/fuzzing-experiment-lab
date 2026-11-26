"""Compatibility entrypoint: always show the current interactive app.py.

Recommended command: python -m streamlit run app.py
"""
from pathlib import Path
import sys
_here = Path(__file__).resolve().parent
if str(_here) not in sys.path:
    sys.path.insert(0, str(_here))
_app = _here / "app.py"
exec(compile(_app.read_text(encoding="utf-8"), str(_app), "exec"), {"__name__": "__main__", "__file__": str(_app)})
