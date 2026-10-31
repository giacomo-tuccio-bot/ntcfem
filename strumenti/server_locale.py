"""Server di sviluppo: stessa pagina e stesse API di Vercel, sul tuo PC.

    python strumenti/server_locale.py        poi apri http://localhost:8000
"""
import importlib.util
import sys
import types
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RADICE))


def _carica(nome):
    spec = importlib.util.spec_from_file_location(nome, RADICE / "api" / f"{nome}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.handler


API = {"/api/calcola": _carica("calcola"), "/api/ottimizza": _carica("ottimizza")}


class Gestore(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(RADICE / "web"), **k)

    def do_POST(self):
        h = API.get(self.path.split("?")[0])
        if h is None:
            self.send_error(404)
            return
        self._invia = types.MethodType(h._invia, self)
        h.do_POST(self)


if __name__ == "__main__":
    porta = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    print(f"ntcfem su http://localhost:{porta}")
    ThreadingHTTPServer(("", porta), Gestore).serve_forever()
