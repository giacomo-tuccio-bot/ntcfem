"""Confronto di sezioni alternative per una trave, a costo minimo (acciaio + cls + casseri).

ATTENZIONE: cambiare la sezione cambia la rigidezza dell'edificio, quindi le
sollecitazioni. Nel modello completo la sezione scelta va rimessa nel calcolo globale
e verificata di nuovo (ciclo: analisi -> ottimizzazione -> analisi ...).
"""
from .armature import ottimizza

# Prezzi di ESEMPIO: sostituire con il proprio prezzario
PREZZI = {"acciaio_euro_kg": 1.60, "cls_euro_m3": 140.0, "casseri_euro_m2": 30.0}


def costo_al_metro(b, h, kg_m, sp=None, prezzi=PREZZI, sporgenza_solaio=0.0):
    p = prezzi
    cls = b * h / 1e6 * p["cls_euro_m3"]
    casseri = (b + 2 * (h - sporgenza_solaio)) / 1e3 * p["casseri_euro_m2"]
    return round(kg_m * p["acciaio_euro_kg"] + cls + casseri, 2)


def confronta(M_Ed, larghezze=(300,), altezze=(500, 550, 600, 650, 700), copriferro=40,
              cls="C25/30", sporgenza_solaio=0.0, prezzi=PREZZI):
    out = []
    for b in larghezze:
        for h in altezze:
            arm = ottimizza(b, h, copriferro, M_Ed, cls, top=1)
            if not arm:
                continue
            a = arm[0]
            out.append({"sezione": f"{b}x{h}", "armatura": a["barre"], "kg_m": a["kg_m"],
                        "x_d": a["x_d"],
                        "euro_m": costo_al_metro(b, h, a["kg_m"], prezzi=prezzi,
                                                 sporgenza_solaio=sporgenza_solaio)})
    return sorted(out, key=lambda r: r["euro_m"])
