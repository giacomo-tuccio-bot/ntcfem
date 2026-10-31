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


def _chiama(metodo, percorso, corpo=b""):
    import io
    stato = {}
    env = {"REQUEST_METHOD": metodo, "PATH_INFO": percorso, "CONTENT_LENGTH": str(len(corpo)),
           "wsgi.input": io.BytesIO(corpo)}
    from ntcfem.server import app
    out = b"".join(app(env, lambda s, h: stato.update(s=s)))
    return stato["s"], out


def test_wsgi_pagina_e_api():
    s, out = _chiama("GET", "/")
    assert s.startswith("200") and b"ntcfem" in out
    s, out = _chiama("POST", "/api/ottimizza", b'{"M_Ed": 150}')
    assert s.startswith("200") and json.loads(out)["soluzioni"]
    s, _ = _chiama("POST", "/api/calcola", b'{"nodi": "rotto"}')
    assert s.startswith("400")
