"""Test dell'ottimizzatore di armature."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ntcfem.norme.ca import Acciaio, Cls, area_barre, momento_resistente  # noqa: E402
from ntcfem.ottimizzazione.armature import ottimizza  # noqa: E402


def test_soluzioni_conformi_e_ordinate():
    sol = ottimizza(300, 600, 40, 300.0)
    assert sol, "nessuna soluzione"
    assert all(s["MRd_kNm"] >= 300.0 and s["x_d"] <= 0.45 for s in sol)
    assert [s["kg_m"] for s in sol] == sorted(s["kg_m"] for s in sol)


def test_non_peggio_di_10fi16():
    c, a = Cls.da_classe("C25/30"), Acciaio(450)
    M, _, _ = momento_resistente(300, 600, 68, area_barre(10, 16), 0, c, a)
    assert ottimizza(300, 600, 40, 0.95 * M)[0]["kg_m"] <= 10 * 0.00617 * 16**2
