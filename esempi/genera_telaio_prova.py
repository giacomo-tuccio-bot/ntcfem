"""Genera esempi/telaio_prova.json: telaio 2 piani, 2x1 campate da 5 m."""
import json
from pathlib import Path

xs, ys, zs = [0.0, 5.0, 10.0], [0.0, 5.0], [0.0, 3.0, 6.0]
nodi, aste, idx = [], [], {}
for k, z in enumerate(zs):
    for y in ys:
        for x in xs:
            nid = f"N{len(nodi) + 1}"
            idx[(x, y, k)] = nid
            nodi.append({"id": nid, "x": x, "y": y, "z": z, "incastro": k == 0})

def asta(i, j, sez, tipo):
    aste.append({"id": f"{'P' if tipo == 'pilastro' else 'T'}{len(aste) + 1}",
                 "i": i, "j": j, "sezione": sez, "tipo": tipo})

for k in range(1, len(zs)):
    for y in ys:
        for x in xs:
            asta(idx[(x, y, k - 1)], idx[(x, y, k)], "P30x30", "pilastro")
for k in range(1, len(zs)):
    for y in ys:
        for a, b in zip(xs[:-1], xs[1:]):
            asta(idx[(a, y, k)], idx[(b, y, k)], "T30x50", "trave")
    for x in xs:
        for a, b in zip(ys[:-1], ys[1:]):
            asta(idx[(x, a, k)], idx[(x, b, k)], "T30x50", "trave")

modello = {
    "descrizione": "Telaio di prova c.a. - 2 piani, 2 campate in X, 1 in Y",
    "nodi": nodi,
    "sezioni": {"P30x30": {"b": 0.30, "h": 0.30, "materiale": "C25/30"},
                "T30x50": {"b": 0.30, "h": 0.50, "materiale": "C25/30"}},
    "aste": aste,
    "impalcati": [{"z": z, "G1": 3.0, "G2": 2.0, "Q": 2.0, "psi2": 0.3} for z in zs[1:]],
    "sismica": {"ag": 0.20, "F0": 2.50, "Tc_star": 0.30, "sottosuolo": "C",
                "topografia": "T1", "q": 3.6, "xi": 0.05,
                "_nota": "parametri di ESEMPIO: sostituire con quelli del sito"},
}
Path(__file__).with_name("telaio_prova.json").write_text(json.dumps(modello, indent=2), encoding="utf-8")
print("Creato telaio_prova.json")
