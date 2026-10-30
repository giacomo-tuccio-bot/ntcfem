"""Combinazioni delle azioni - NTC 2018 par. 2.5.3, coefficienti Tab. 2.5.I e 2.6.I (STR)."""
from ..modello import carica_dati

_T = carica_dati("ntc2018.json")


def psi(categoria):
    """(psi0, psi1, psi2) per la categoria di azione variabile (Tab. 2.5.I)."""
    return tuple(_T["psi"][categoria])


def combinazioni(G1, G2, variabili):
    """Valore combinato di un effetto (carico, momento, taglio...) per ogni combinazione.

    G1, G2: effetti dei permanenti; variabili: lista di (Qk, categoria).
    Restituisce dict {nome: valore}; per l'SLU ogni variabile e' presa a turno come principale.
    Si considerano tutte le azioni sfavorevoli (effetti dello stesso segno).
    """
    gG1, gG2, gQ = (_T["gamma_STR"][k][1] for k in ("G1", "G2", "Q"))
    out = {}
    if not variabili:
        variabili = [(0.0, "A_residenziale")]
    for i, (Qp, catp) in enumerate(variabili):
        acc = [(Q, psi(c)) for j, (Q, c) in enumerate(variabili) if j != i]
        out[f"SLU_{i + 1}"] = gG1 * G1 + gG2 * G2 + gQ * Qp + sum(gQ * p[0] * Q for Q, p in acc)      # 2.5.1
        out[f"SLE_rara_{i + 1}"] = G1 + G2 + Qp + sum(p[0] * Q for Q, p in acc)                       # 2.5.2
        out[f"SLE_frequente_{i + 1}"] = G1 + G2 + psi(catp)[1] * Qp + sum(p[2] * Q for Q, p in acc)   # 2.5.3
    out["SLE_quasi_permanente"] = G1 + G2 + sum(psi(c)[2] * Q for Q, c in variabili)                 # 2.5.4
    return out


def inviluppo(comb, prefisso):
    vals = {k: v for k, v in comb.items() if k.startswith(prefisso)}
    k = max(vals, key=lambda n: abs(vals[n]))
    return k, vals[k]
