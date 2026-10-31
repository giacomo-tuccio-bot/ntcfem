"""API Vercel: POST /api/ottimizza  {"M_Ed": kNm, "larghezze": [...], "altezze": [...], "prezzi": {...}}"""
import json
import sys
from http.server import BaseHTTPRequestHandler
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ntcfem.web import ottimizza_trave  # noqa: E402


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            n = int(self.headers.get("content-length", 0))
            self._invia(200, ottimizza_trave(json.loads(self.rfile.read(n))))
        except Exception as e:
            self._invia(400, {"errore": str(e)})

    def _invia(self, codice, dati):
        corpo = json.dumps(dati, ensure_ascii=False).encode("utf-8")
        self.send_response(codice)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)
