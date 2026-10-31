"""Ottimizzazione delle armature longitudinali di una sezione rettangolare in c.a.

Data la sollecitazione M_Ed, prova tutte le disposizioni con uno o due diametri
(eventualmente su due strati) e restituisce quelle conformi ordinate per peso di acciaio.
Le sollecitazioni non cambiano (la rigidezza del modello non dipende dalle barre),
quindi non serve rifare l'analisi globale.

Vincoli controllati:
- MRd >= M_Ed                                   (4.1.2.3.4.2)
- As >= As,min = 0.26 fctm/fyk b d >= 0.0013 b d (4.1.6.1.1)
- As <= 0.04 Ac                                  (4.1.6.1.1)
- x/d <= xd_max (default 0.45) per garantire duttilita'
- interferro netto >= max(diam, 20 mm, dg + 5 mm) (4.1.6.1.4 / EC2 8.2)
"""
from itertools import combinations_with_replacement

from ..norme.ca import Acciaio, Cls, area_barre, momento_resistente

DIAMETRI = (12, 14, 16, 18, 20, 22, 24)
KG_M = {d: 0.00617 * d**2 for d in DIAMETRI}      # peso barra [kg/m] = 7850*pi*d^2/4


def entra_in_uno_strato(b, copriferro, staffa, barre, dg=20):
    """True se le barre stanno in una fila con interferro regolamentare."""
    s_min = max(max(barre), 20, dg + 5)
    larghezza = sum(barre) + (len(barre) - 1) * s_min
    return larghezza <= b - 2 * (copriferro + staffa)


def disposizioni(n_max=12):
    """Tutte le combinazioni di n barre con al massimo 2 diametri diversi."""
    for n in range(2, n_max + 1):
        for comb in combinations_with_replacement(DIAMETRI, n):
            if len(set(comb)) <= 2:
                yield comb


def ottimizza(b, h, copriferro, M_Ed, cls="C25/30", fyk=450, As2=0.0, staffa=8, n_max=12, top=5, xd_max=0.45):
    c, a = Cls.da_classe(cls), Acciaio(fyk)
    risultati = []
    for barre in disposizioni(n_max):
        strati = 1 if entra_in_uno_strato(b, copriferro, staffa, barre) else 2
        if strati == 2:
            meta = sorted(barre, reverse=True)
            if not entra_in_uno_strato(b, copriferro, staffa, meta[: (len(meta) + 1) // 2]):
                continue
        # baricentro armature: con 2 strati si arretra di (diam + 25 mm)/2 circa
        dmax = max(barre)
        cc = copriferro + staffa + dmax / 2 + (0 if strati == 1 else (dmax + 25) / 2)
        d = h - cc
        As = sum(area_barre(1, x) for x in barre)
        fctm = 0.30 * c.fck ** (2 / 3)
        if As < max(0.26 * fctm / fyk, 0.0013) * b * d or As > 0.04 * b * h:
            continue
        MRd, x, xd = momento_resistente(b, h, cc, As, As2, c, a)
        if MRd < M_Ed or xd > xd_max:
            continue
        risultati.append({"barre": _testo(barre), "strati": strati, "As_mm2": round(As),
                          "kg_m": round(sum(KG_M[x] for x in barre), 2), "MRd_kNm": round(MRd, 1),
                          "sfruttamento": round(M_Ed / MRd, 3), "x_d": round(xd, 3),
                          "n_barre": len(barre)})
    # a parita' di peso: meno barre e un solo strato (piu' facili da posare)
    risultati.sort(key=lambda r: (r["kg_m"], r["strati"], r["n_barre"]))
    return risultati[:top]


def _testo(barre):
    from collections import Counter
    return " + ".join(f"{n}Ø{d}" for d, n in sorted(Counter(barre).items(), reverse=True))
