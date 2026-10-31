"""Solutore a telaio 3D (metodo degli spostamenti) con impalcati rigidi.

Elemento trave di Eulero-Bernoulli a 12 gdl, deformabilita' a taglio trascurata.
Gdl per nodo: ux, uy, uz, rx, ry, rz.
"""
import numpy as np

from .modello import proprieta_rettangolo


def k_locale(E, G, L, A, Iy, Iz, J):
    k = np.zeros((12, 12))
    EA, GJ = E * A / L, G * J / L
    k[0, 0] = k[6, 6] = EA
    k[0, 6] = k[6, 0] = -EA
    k[3, 3] = k[9, 9] = GJ
    k[3, 9] = k[9, 3] = -GJ
    # flessione nel piano x-y locale (Iz)
    a, b, c, d = 12 * E * Iz / L**3, 6 * E * Iz / L**2, 4 * E * Iz / L, 2 * E * Iz / L
    for i, j, v in [(1, 1, a), (1, 5, b), (1, 7, -a), (1, 11, b), (5, 5, c), (5, 7, -b),
                    (5, 11, d), (7, 7, a), (7, 11, -b), (11, 11, c)]:
        k[i, j] = k[j, i] = v
    # flessione nel piano x-z locale (Iy)
    a, b, c, d = 12 * E * Iy / L**3, 6 * E * Iy / L**2, 4 * E * Iy / L, 2 * E * Iy / L
    for i, j, v in [(2, 2, a), (2, 4, -b), (2, 8, -a), (2, 10, -b), (4, 4, c), (4, 8, b),
                    (4, 10, d), (8, 8, a), (8, 10, b), (10, 10, c)]:
        k[i, j] = k[j, i] = v
    return k


def matrice_rotazione(pi, pj):
    """Asse x locale lungo l'asta; asse z locale verticale per le travi,
    globale X come riferimento per le aste verticali."""
    ex = (pj - pi) / np.linalg.norm(pj - pi)
    ref = np.array([1.0, 0, 0]) if abs(ex[2]) > 0.99 else np.array([0, 0, 1.0])
    ey = np.cross(ref, ex)
    ey /= np.linalg.norm(ey)
    ez = np.cross(ex, ey)
    R = np.vstack([ex, ey, ez])
    T = np.zeros((12, 12))
    for n in range(4):
        T[3 * n:3 * n + 3, 3 * n:3 * n + 3] = R
    return T


def rigidezza_globale(mod):
    n = len(mod.ids)
    K = np.zeros((6 * n, 6 * n))
    for a in mod.aste:
        s = mod.sezioni[a["sezione"]]
        mat = mod.materiali[s["materiale"]]
        i, j = mod.indice[a["i"]], mod.indice[a["j"]]
        pi, pj = mod.coord[i], mod.coord[j]
        A, I_forte, I_debole, J = proprieta_rettangolo(s["b"], s["h"])
        # h = dimensione nel piano verticale per le travi, lungo X globale per i pilastri
        T = matrice_rotazione(pi, pj)
        kg = T.T @ k_locale(mat.E, mat.G, mod.lunghezza(a), A, I_forte, I_debole, J) @ T
        dofs = np.r_[6 * i:6 * i + 6, 6 * j:6 * j + 6]
        K[np.ix_(dofs, dofs)] += kg
    return K


def condensa_impalcati(mod, K, masse):
    """Applica il vincolo di impalcato rigido e condensa sui gdl dei baricentri.

    Restituisce Kc (3*nimp x 3*nimp), Mc e la matrice Tr per risalire ai gdl completi.
    """
    col = {}
    for k in range(len(masse)):
        for d in ("ux", "uy", "rz"):
            col[("M", k, d)] = len(col)
    liberi = []
    for nid in mod.ids:
        nodo = mod.nodi[nid]
        if nodo.get("incastro"):
            continue
        k = mod.livello(nodo["z"])
        dl = ("uz", "rx", "ry") if k is not None else ("ux", "uy", "uz", "rx", "ry", "rz")
        for d in dl:
            col[(nid, d)] = len(col)
        liberi.append((nid, k))

    pos = {"ux": 0, "uy": 1, "uz": 2, "rx": 3, "ry": 4, "rz": 5}
    Tr = np.zeros((K.shape[0], len(col)))
    for nid, k in liberi:
        b0 = 6 * mod.indice[nid]
        for d, p in pos.items():
            if (nid, d) in col:
                Tr[b0 + p, col[(nid, d)]] = 1
        if k is not None:
            x, y = mod.nodi[nid]["x"], mod.nodi[nid]["y"]
            xg, yg = masse[k]["xg"], masse[k]["yg"]
            cx, cy, cr = (col[("M", k, d)] for d in ("ux", "uy", "rz"))
            Tr[b0 + 0, cx] = 1
            Tr[b0 + 0, cr] = -(y - yg)
            Tr[b0 + 1, cy] = 1
            Tr[b0 + 1, cr] = x - xg
            Tr[b0 + 5, cr] = 1

    Kr = Tr.T @ K @ Tr
    m = list(range(3 * len(masse)))
    s = list(range(3 * len(masse), len(col)))
    Kms = Kr[np.ix_(m, s)]
    Kss = Kr[np.ix_(s, s)]
    Kc = Kr[np.ix_(m, m)] - Kms @ np.linalg.solve(Kss, Kms.T)
    Mc = np.diag(np.concatenate([[d["m"], d["m"], d["Jp"]] for d in masse]))
    return Kc, Mc


def analisi_modale(Kc, Mc):
    # Problema generalizzato K phi = w2 M phi con M diagonale: si riduce a uno standard
    # con M^-1/2 K M^-1/2 (solo numpy, cosi' gira anche online senza scipy).
    s = 1.0 / np.sqrt(np.diag(Mc))
    w2, V = np.linalg.eigh(s[:, None] * Kc * s[None, :])
    Phi = s[:, None] * V            # Phi normalizzati rispetto alle masse
    omega = np.sqrt(w2)
    n = len(omega)
    rX = np.tile([1.0, 0, 0], n // 3)
    rY = np.tile([0, 1.0, 0], n // 3)
    Mtot = sum(Mc[3 * k, 3 * k] for k in range(n // 3))
    gX = Phi.T @ Mc @ rX
    gY = Phi.T @ Mc @ rY
    return dict(omega=omega, T=2 * np.pi / omega, Phi=Phi, gX=gX, gY=gY,
                mX=gX**2 / Mtot, mY=gY**2 / Mtot)
