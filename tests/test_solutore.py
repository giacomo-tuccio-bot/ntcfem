"""Test di validazione. Eseguire con:  python -m pytest   (oppure  python tests/test_solutore.py)"""
import sys
from pathlib import Path

import numpy as np

RADICE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RADICE))

from ntcfem.calcolo import esegui                       # noqa: E402
from ntcfem.modello import Materiale, Modello, proprieta_rettangolo  # noqa: E402
from ntcfem.sismica import Sd, parametri_spettro         # noqa: E402
from ntcfem.solutore import k_locale, matrice_rotazione  # noqa: E402


def _mensola(p_j, b, h, F_dir):
    mat = Materiale.calcestruzzo("C25/30")
    A, If, Id, J = proprieta_rettangolo(b, h)
    pi, pj = np.zeros(3), np.array(p_j, float)
    L = np.linalg.norm(pj)
    T = matrice_rotazione(pi, pj)
    K = T.T @ k_locale(mat.E, mat.G, L, A, If, Id, J) @ T
    F = np.zeros(6)
    F[F_dir] = 10.0
    return np.linalg.solve(K[6:, 6:], F)[F_dir], mat.E, L, If


def test_mensola_pilastro():
    u, E, L, I = _mensola([0, 0, 3], 0.3, 0.3, 0)
    assert np.isclose(u, 10 * L**3 / (3 * E * I), rtol=1e-9)


def test_mensola_trave_verticale():
    u, E, L, I = _mensola([5, 0, 0], 0.3, 0.5, 2)
    assert np.isclose(u, 10 * L**3 / (3 * E * I), rtol=1e-9)


def test_spettro_plateau():
    p = parametri_spettro(0.20, 2.5, 0.30, "C", "T1")
    assert np.isclose(p["S"], 1.40)
    assert np.isclose(Sd(0.3, 0.20, 2.5, p, 3.6)[0], 0.20 * 1.4 * 2.5 / 3.6)


def test_regressione_telaio_prova():
    """Valori di riferimento del telaio di prova (v0.1.0). Se cambiano, capire perche'."""
    r = esegui(Modello.da_file(RADICE / "esempi" / "telaio_prova.json"))
    T = [m["T_s"] for m in r["modi"]]
    assert np.isclose(T[0], 0.335, atol=0.001)
    assert np.isclose(T[1], 0.328, atol=0.001)
    assert np.isclose(r["W_totale_kN"], 883.2, atol=0.1)
    assert np.isclose(r["taglio_base_kN"]["X"], 159.6, atol=0.2)
    assert r["massa_partecipante_tot"]["X"] > 99.9


if __name__ == "__main__":
    for nome, f in list(globals().items()):
        if nome.startswith("test_"):
            f()
            print("OK ", nome)
