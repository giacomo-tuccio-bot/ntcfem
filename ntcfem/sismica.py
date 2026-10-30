"""Spettro di progetto NTC 2018 (par. 3.2.3) e analisi modale con spettro di risposta."""
import numpy as np

from .modello import carica_dati

g = 9.81


def parametri_spettro(ag, F0, Tc_star, sottosuolo, topografia):
    tab = carica_dati("ntc2018.json")
    s = tab["sottosuolo"][sottosuolo]
    Ss = s["Ss"][0] - s["Ss"][1] * F0 * ag
    Ss = min(max(Ss, s["Ss_lim"][0]), s["Ss_lim"][1])
    Cc = s["Cc"][0] * Tc_star ** s["Cc"][1] if sottosuolo != "A" else 1.0
    S = Ss * tab["topografia"][topografia]
    TC = Cc * Tc_star
    return dict(S=S, Ss=Ss, Cc=Cc, TB=TC / 3, TC=TC, TD=4.0 * ag + 1.6)


def Sd(T, ag, F0, p, q):
    """Ordinata dello spettro di progetto SLU in g (eta = 1/q, limite 0.2 ag)."""
    S, TB, TC, TD = p["S"], p["TB"], p["TC"], p["TD"]
    eta = 1.0 / q
    out = []
    for t in np.atleast_1d(T):
        if t < TB:
            v = ag * S * eta * F0 * (t / TB + 1 / (eta * F0) * (1 - t / TB))
        elif t < TC:
            v = ag * S * eta * F0
        elif t < TD:
            v = max(ag * S * eta * F0 * TC / t, 0.2 * ag)
        else:
            v = max(ag * S * eta * F0 * TC * TD / t**2, 0.2 * ag)
        out.append(v)
    return np.array(out)


def coeff_cqc(omega, xi=0.05):
    n = len(omega)
    rho = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            b = omega[j] / omega[i]
            rho[i, j] = 8 * xi**2 * (1 + b) * b**1.5 / ((1 - b**2) ** 2 + 4 * xi**2 * b * (1 + b) ** 2)
    return rho


def cqc(R, rho):
    """Combina risposte modali R (nmodi x ...) con la regola CQC."""
    return np.sqrt(np.abs(np.einsum("i...,ij,j...->...", R, rho, R)))


def analisi_spettrale(modale, sis):
    p = parametri_spettro(sis["ag"], sis["F0"], sis["Tc_star"], sis["sottosuolo"], sis["topografia"])
    sd = Sd(modale["T"], sis["ag"], sis["F0"], p, sis["q"])
    rho = coeff_cqc(modale["omega"], sis.get("xi", 0.05))
    Phi, w = modale["Phi"], modale["omega"]
    res = {"spettro": p, "Sd": sd}
    for dir_, gam in (("X", modale["gX"]), ("Y", modale["gY"])):
        U = np.array([Phi[:, i] * gam[i] * sd[i] * g / w[i] ** 2 for i in range(len(w))])
        Vb = np.array([gam[i] ** 2 * sd[i] * g for i in range(len(w))])
        res[dir_] = dict(U=cqc(U, rho), Vb=float(cqc(Vb, rho)))
    return res
