"""Gestione del catalogo dei calcoli (docs/catalogo_calcoli.txt -> dati/catalogo.json).

    python strumenti/catalogo.py genera   crea/aggiorna dati/catalogo.json mantenendo gli stati
    python strumenti/catalogo.py stato    mostra l'avanzamento per fase e per categoria

Stati: da_fare | in_corso | parziale | fatto | validato (= confrontato con Edilus)
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
TXT = RADICE / "docs" / "catalogo_calcoli.txt"
JSON = RADICE / "dati" / "catalogo.json"

# Fase di default per categoria (vedi docs/ROADMAP.md)
FASE_CATEGORIA = {1: 2, 2: 2, 3: 2, 4: 6, 5: 6, 6: 5, 7: 5, 8: 5, 9: 6, 10: 7, 11: 2,
                  12: 2, 13: 5, 14: 6, 15: 6, 16: 4, 17: 6, 18: 3, 20: 7, 21: 7}
# Voci anticipate rispetto alla loro categoria (le piu' frequenti nello studio)
ANTICIPATE = {
    "Muri di sostegno in cemento armato a mensola.": 2,
    "Muri controterra di piani interrati.": 2,
    "Verifiche di scorrimento, ribaltamento e capacità portante.": 2,
    "Calcolo della capacità portante.": 2,
    "Realizzazione di cerchiature metalliche.": 2,
    "Apertura di vani in muratura portante.": 2,
    "Allargamento di porte e finestre.": 2,
    "Travi IPE, HEA, HEB.": 2,
    "Pilastri in profilati HEA, HEB, HEM.": 2,
    "Travi in legno massiccio.": 2,
    "Travi in legno lamellare.": 2,
}
RITARDATE = {k: 7 for k in [
    "Elementi in cemento armato precompresso, quando impiegati nell’edilizia.",
    "Travi curve.", "Travi parete (travi alte).", "Scale elicoidali.",
    "Scale sospese con tiranti.", "Scale a sbalzo con struttura nascosta.",
    "Analisi dinamica non lineare (time history).", "Verifica di edifici con isolamento alla base.",
    "Verifica di sistemi di dissipazione sismica.", "Coperture curve.", "Pensiline sospese."]}
FATTI = {"Analisi dinamica modale con spettro di risposta.": "parziale",
         "Calcolo del periodo proprio di vibrazione.": "fatto"}


def leggi_txt():
    voci, cat, nome_cat = [], None, None
    for riga in TXT.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^(\d+)\.\s+(.+)$", riga.strip())
        if m and not riga.startswith("*"):
            cat, nome_cat = int(m.group(1)), m.group(2).strip()
            continue
        if riga.startswith("* ") and cat:
            testo = riga[2:].strip()
            fase = ANTICIPATE.get(testo) or RITARDATE.get(testo) or FASE_CATEGORIA.get(cat, 7)
            voci.append({"id": f"C{cat:02d}.{sum(v['categoria'] == cat for v in voci) + 1:02d}",
                         "categoria": cat, "nome_categoria": nome_cat, "voce": testo,
                         "fase": fase, "stato": FATTI.get(testo, "da_fare"), "modulo": None})
    return voci


def genera():
    nuove = leggi_txt()
    if JSON.exists():
        vecchie = {v["voce"]: v for v in json.loads(JSON.read_text(encoding="utf-8"))["voci"]}
        for v in nuove:
            if v["voce"] in vecchie:
                for k in ("stato", "modulo", "fase"):
                    v[k] = vecchie[v["voce"]][k]
    JSON.write_text(json.dumps({"voci": nuove}, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"{len(nuove)} voci scritte in {JSON.relative_to(RADICE)}")


def stato():
    voci = json.loads(JSON.read_text(encoding="utf-8"))["voci"]
    ok = lambda v: v["stato"] in ("fatto", "validato")
    print(f"Totale: {sum(map(ok, voci))}/{len(voci)} voci completate\n")
    for f in sorted({v["fase"] for v in voci}):
        vf = [v for v in voci if v["fase"] == f]
        print(f"Fase {f}: {sum(map(ok, vf)):3d}/{len(vf):3d}")
    print()
    c = Counter((v["categoria"], v["nome_categoria"]) for v in voci)
    for (n, nome), tot in sorted(c.items()):
        fatte = sum(ok(v) for v in voci if v["categoria"] == n)
        print(f"{n:2d}. {nome[:52]:52s} {fatte:3d}/{tot:3d}")


if __name__ == "__main__":
    {"genera": genera, "stato": stato}[sys.argv[1] if len(sys.argv) > 1 else "stato"]()
