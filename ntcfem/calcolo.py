"""Esegue l'intera analisi su un modello e produce i risultati (dict, JSON, testo)."""
import json
from pathlib import Path

import numpy as np

from . import __version__
from .modello import Modello
from .sismica import analisi_spettrale
from .solutore import analisi_modale, condensa_impalcati, rigidezza_globale


def esegui(mod: Modello):
    masse = mod.masse_impalcati()
    K = rigidezza_globale(mod)
    Kc, Mc = condensa_impalcati(mod, K, masse)
    modale = analisi_modale(Kc, Mc)
    spet = analisi_spettrale(modale, mod.sismica)

    W = sum(d["W"] for d in masse)
    quote = [0.0] + [d["z"] for d in masse]
    piani = []
    for dir_, d in (("X", 0), ("Y", 1)):
        u = [float(spet[dir_]["U"][3 * k + d]) * 1000 for k in range(len(masse))]
        for k, uk in enumerate(u):
            du = uk - (u[k - 1] if k else 0.0)
            h = quote[k + 1] - quote[k]
            piani.append(dict(direzione=dir_, impalcato=k + 1, spostamento_mm=round(uk, 3),
                              interpiano_mm=round(du, 3), drift_perc=round(du / (h * 10), 4)))

    return {
        "versione_software": __version__,
        "impalcati": [{"z": d["z"], "W_kN": round(d["W"], 2), "m_t": round(d["m"], 3)} for d in masse],
        "W_totale_kN": round(W, 2),
        "modi": [{"modo": i + 1, "T_s": round(float(modale["T"][i]), 4),
                  "Mx_perc": round(100 * float(modale["mX"][i]), 2),
                  "My_perc": round(100 * float(modale["mY"][i]), 2),
                  "Sd_g": round(float(spet["Sd"][i]), 4)} for i in range(len(modale["T"]))],
        "massa_partecipante_tot": {"X": round(100 * float(modale["mX"].sum()), 2),
                                   "Y": round(100 * float(modale["mY"].sum()), 2)},
        "spettro": {k: round(v, 4) for k, v in spet["spettro"].items()} | mod.sismica,
        "taglio_base_kN": {"X": round(spet["X"]["Vb"], 2), "Y": round(spet["Y"]["Vb"], 2)},
        "spostamenti": piani,
        "note": ["Spostamenti dallo spettro di progetto (ridotto di q): per lo SLV "
                 "moltiplicare per mu_d (NTC 7.3.3.3); i drift vanno verificati allo SLD."],
    }


def come_testo(r):
    L = ["ANALISI MODALE E SPETTRO NTC 2018  (ntcfem v%s)" % r["versione_software"], "=" * 62]
    for k, d in enumerate(r["impalcati"], 1):
        L.append(f"Impalcato {k} (z={d['z']:.2f} m): W = {d['W_kN']:8.1f} kN   m = {d['m_t']:7.2f} t")
    L.append(f"Peso sismico totale W = {r['W_totale_kN']:.1f} kN\n")
    L.append(f"{'Modo':>4} {'T [s]':>8} {'Mx %':>7} {'My %':>7} {'Sd/g':>7}")
    for m in r["modi"]:
        L.append(f"{m['modo']:>4} {m['T_s']:8.3f} {m['Mx_perc']:7.1f} {m['My_perc']:7.1f} {m['Sd_g']:7.3f}")
    t = r["massa_partecipante_tot"]
    L.append(f"{'Tot':>4} {'':>8} {t['X']:7.1f} {t['Y']:7.1f}\n")
    s = r["spettro"]
    L.append(f"Spettro SLV: ag={s['ag']}g F0={s['F0']} Tc*={s['Tc_star']}s suolo {s['sottosuolo']} "
             f"S={s['S']:.3f} TB={s['TB']:.3f} TC={s['TC']:.3f} TD={s['TD']:.3f} q={s['q']}\n")
    for dir_ in ("X", "Y"):
        Vb = r["taglio_base_kN"][dir_]
        L.append(f"Sisma {dir_} (CQC): taglio alla base = {Vb:.1f} kN ({100 * Vb / r['W_totale_kN']:.1f}% di W)")
        for p in r["spostamenti"]:
            if p["direzione"] == dir_:
                L.append(f"   impalcato {p['impalcato']}: u = {p['spostamento_mm']:6.2f} mm   "
                         f"interpiano = {p['interpiano_mm']:6.2f} mm ({p['drift_perc']:.3f}% h)")
    L += [""] + r["note"]
    return "\n".join(L)


def salva(r, cartella, nome):
    cartella = Path(cartella)
    cartella.mkdir(parents=True, exist_ok=True)
    (cartella / f"{nome}_risultati.json").write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
    (cartella / f"{nome}_risultati.txt").write_text(come_testo(r), encoding="utf-8")
    return cartella / f"{nome}_risultati.json"
