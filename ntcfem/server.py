"""Applicazione web (WSGI, solo libreria standard): pagina + API di calcolo.

Usata da Vercel (pyproject.toml -> [tool.vercel] entrypoint = "ntcfem.server:app")
e in locale da strumenti/server_locale.py.

    GET  /               pagina web/index.html
    POST /api/calcola    corpo = modello JSON  -> risultati
    POST /api/ottimizza  {"M_Ed", "larghezze", "altezze", "prezzi"} -> soluzioni
"""
import json
from pathlib import Path

from .web import calcola, ottimizza_trave

PAGINA = Path(__file__).resolve().parent.parent / "web" / "index.html"
API = {"/api/calcola": calcola, "/api/ottimizza": ottimizza_trave}
MAX_CORPO = 5_000_000   # 5 MB


def _risposta(start_response, codice, corpo, tipo):
    start_response(codice, [("Content-Type", tipo), ("Content-Length", str(len(corpo)))])
    return [corpo]


def _json(start_response, codice, dati):
    return _risposta(start_response, codice, json.dumps(dati, ensure_ascii=False).encode("utf-8"),
                     "application/json; charset=utf-8")


def app(environ, start_response):
    percorso = environ.get("PATH_INFO", "/")
    metodo = environ.get("REQUEST_METHOD", "GET")

    if metodo == "GET" and percorso in ("/", "/index.html"):
        return _risposta(start_response, "200 OK", PAGINA.read_bytes(), "text/html; charset=utf-8")

    if percorso in API:
        if metodo != "POST":
            return _json(start_response, "405 Method Not Allowed", {"errore": "usa POST"})
        try:
            n = int(environ.get("CONTENT_LENGTH") or 0)
            if n > MAX_CORPO:
                raise ValueError("Richiesta troppo grande")
            dati = json.loads(environ["wsgi.input"].read(n) or b"{}")
            return _json(start_response, "200 OK", API[percorso](dati))
        except Exception as e:      # errore leggibile nella pagina
            return _json(start_response, "400 Bad Request", {"errore": str(e)})

    return _json(start_response, "404 Not Found", {"errore": f"{percorso} non trovato"})
