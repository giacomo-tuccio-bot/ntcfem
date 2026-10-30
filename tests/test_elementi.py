"""Test delle verifiche di sezione e dei moduli elemento, confrontati con calcoli a mano."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ntcfem.elementi import TraveCaAppoggiata                      # noqa: E402
from ntcfem.norme.ca import (Acciaio, Cls, area_barre, momento_resistente,  # noqa: E402
                             taglio_con_staffe, taglio_senza_staffe)
from ntcfem.norme.combinazioni import combinazioni                 # noqa: E402

C25, B450 = Cls.da_classe("C25/30"), Acciaio(450)
As3f16 = area_barre(3, 16)


def test_combinazioni_slu():
    c = combinazioni(3.75, 6.0, [(4.0, "A_residenziale")])
    assert np.isclose(c["SLU_1"], 1.3 * 3.75 + 1.5 * 6 + 1.5 * 4)
    assert np.isclose(c["SLE_quasi_permanente"], 3.75 + 6 + 0.3 * 4)


def test_momento_semplice_armatura():
    # a mano: x = As fyd / (0.8 b fcd); M = As fyd (d - 0.4x)
    fyd, fcd = 450 / 1.15, 0.85 * 25 / 1.5
    x = As3f16 * fyd / (0.8 * 300 * fcd)
    M = As3f16 * fyd * (460 - 0.4 * x) / 1e6
    MRd, xc, _ = momento_resistente(300, 500, 40, As3f16, 0.0, C25, B450)
    assert np.isclose(xc, x, rtol=1e-6) and np.isclose(MRd, M, rtol=1e-6)


def test_taglio_senza_staffe():
    assert np.isclose(taglio_senza_staffe(300, 460, As3f16, C25), 60.98, atol=0.05)


def test_taglio_con_staffe():
    VRd, VRsd, VRcd, ct = taglio_con_staffe(300, 460, area_barre(2, 8), 200, C25, B450)
    assert np.isclose(ct, 2.5) and np.isclose(VRd, 203.6, atol=0.1)


def test_trave_appoggiata():
    t = TraveCaAppoggiata({"L": 5.0, "b": 300, "h": 500, "copriferro": 40, "cls": "C25/30",
                           "g1": 0.0, "g2": 6.0, "q": 4.0, "categoria_q": "A_residenziale",
                           "armatura_inf": [3, 16], "armatura_sup": None, "staffe": [2, 8, 200]})
    r = t.risultati()
    assert np.isclose(r["valori"]["M_Ed_kNm"], 19.875 * 25 / 8, atol=0.01)
    assert r["esito_globale"] == "OK"


if __name__ == "__main__":
    for nome, f in list(globals().items()):
        if nome.startswith("test_"):
            f()
            print("OK ", nome)
