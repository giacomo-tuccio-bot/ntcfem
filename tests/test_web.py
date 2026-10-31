"""Test delle funzioni usate dalle API web."""
import json
import sys
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RADICE))

from ntcfem.web import calcola, ottimizza_trave  # noqa: E402


def test_api_calcola():
    r = calcola(json.loads((RADICE / "esempi" / "telaio_prova.json").read_text()))
    assert abs(r["modi"][0]["T_s"] - 0.335) < 0.001


def test_api_ottimizza_prezzi():
    r = ottimizza_trave({"M_Ed": 180, "prezzi": {"acciaio_euro_kg": 5}})
    assert r["prezzi"]["acciaio_euro_kg"] == 5 and r["soluzioni"]
