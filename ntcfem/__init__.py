"""ntcfem - calcolo strutturale di telai in c.a. secondo NTC 2018 (prototipo)."""
from pathlib import Path

try:
    __version__ = (Path(__file__).resolve().parent.parent / "VERSION").read_text().strip()
except OSError:
    __version__ = "sconosciuta"
