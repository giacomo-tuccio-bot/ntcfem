"""Server di sviluppo: la stessa app che gira su Vercel, sul tuo PC.

    python strumenti/server_locale.py        poi apri http://localhost:8000
"""
import sys
from pathlib import Path
from wsgiref.simple_server import make_server

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ntcfem.server import app  # noqa: E402

if __name__ == "__main__":
    porta = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    print(f"ntcfem su http://localhost:{porta}")
    make_server("", porta, app).serve_forever()
