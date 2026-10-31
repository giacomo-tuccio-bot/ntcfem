"""Funzioni chiamate dalle API web (Vercel) e dal server locale di sviluppo."""
from .calcolo import esegui
from .modello import Modello
from .ottimizzazione.sezioni import PREZZI, confronta

LIMITE_NODI = 600     # protezione del server da modelli troppo grandi


def calcola(modello: dict) -> dict:
    if len(modello.get("nodi", [])) > LIMITE_NODI:
        raise ValueError(f"Modello troppo grande (max {LIMITE_NODI} nodi)")
    return esegui(Modello(modello))


def ottimizza_trave(d: dict) -> dict:
    prezzi = PREZZI | {k: float(v) for k, v in d.get("prezzi", {}).items()}
    alt = d.get("altezze") or [400, 450, 500, 550, 600, 650, 700]
    lar = d.get("larghezze") or [300]
    sol = confronta(float(d["M_Ed"]), larghezze=[int(x) for x in lar], altezze=[int(x) for x in alt],
                    copriferro=int(d.get("copriferro", 40)), cls=d.get("cls", "C25/30"), prezzi=prezzi)
    return {"soluzioni": sol, "prezzi": prezzi}
