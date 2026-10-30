"""Trave in c.a. semplicemente appoggiata con carico uniforme (primo modulo di esempio).

Dati (dict):
  L [m], b, h, copriferro [mm], cls "C25/30", acciaio fyk [MPa]
  g1, g2 [kN/m] (g1 senza peso proprio: viene aggiunto), q [kN/m], categoria_q
  armatura_inf: [n, diam], armatura_sup: [n, diam], staffe: [bracci, diam, passo mm]
"""
from ..norme.ca import Acciaio, Cls, area_barre, momento_resistente, taglio_con_staffe, taglio_senza_staffe
from ..norme.combinazioni import combinazioni, inviluppo
from ..modello import Materiale
from .base import ElementoCalcolo, Verifica, registra


@registra("C01.07")   # Travi semplicemente appoggiate
class TraveCaAppoggiata(ElementoCalcolo):
    titolo = "Trave in c.a. semplicemente appoggiata"

    def calcola(self):
        d = self.dati
        L, b, h, c = d["L"], d["b"], d["h"], d["copriferro"]
        cls, acc = Cls.da_classe(d["cls"]), Acciaio(d.get("fyk", 450))
        pp = b * h / 1e6 * 25.0                                   # peso proprio kN/m
        g1 = d["g1"] + pp
        comb = combinazioni(g1, d["g2"], [(d["q"], d.get("categoria_q", "A_residenziale"))])
        nome_slu, q_slu = inviluppo(comb, "SLU")
        M_Ed, V_Ed = q_slu * L**2 / 8, q_slu * L / 2

        As = area_barre(*d["armatura_inf"])
        As2 = area_barre(*d["armatura_sup"]) if d.get("armatura_sup") else 0.0
        dd = h - c
        MRd, x, xd = momento_resistente(b, h, c, As, As2, cls, acc)
        if d.get("staffe"):
            nb, fi, s = d["staffe"]
            VRd, VRsd, VRcd, ct = taglio_con_staffe(b, dd, area_barre(nb, fi), s, cls, acc)
            rif_v = "4.1.2.3.5.2"
            self.valori["cot_theta"] = round(ct, 3)
        else:
            VRd, rif_v = taglio_senza_staffe(b, dd, As, cls), "4.1.2.3.5.1"

        # freccia elastica a sezione interamente reagente (indicativa, SLE quasi permanente)
        E = Materiale.calcestruzzo(d["cls"]).E                   # kN/m2
        I = b / 1e3 * (h / 1e3) ** 3 / 12
        f = 5 * comb["SLE_quasi_permanente"] * L**4 / (384 * E * I) * 1000   # mm

        self.valori.update({"peso_proprio_kN_m": round(pp, 2), "q_SLU_kN_m": round(q_slu, 2),
                            "M_Ed_kNm": round(M_Ed, 2), "V_Ed_kN": round(V_Ed, 2),
                            "As_mm2": round(As, 1), "x_mm": round(x, 1), "x_d": round(xd, 3),
                            "freccia_qp_mm": round(f, 2)})
        self.verifiche = [
            Verifica("Flessione in mezzeria", M_Ed, MRd, "kNm", "4.1.2.3.4.2", nome_slu),
            Verifica("Taglio all'appoggio", V_Ed, VRd, "kN", rif_v, nome_slu),
            Verifica("Freccia elastica L/250 (indicativa)", f, L * 1000 / 250, "mm", "4.1.2.2.2",
                     "SLE_quasi_permanente"),
        ]
        if xd > 0.45:
            self.note.append(f"x/d = {xd:.2f} > 0.45: duttilita' ridotta, valutare armatura compressa.")
        self.note.append("Freccia calcolata a sezione non fessurata e senza viscosita': "
                         "valore indicativo, la verifica completa va fatta a sezione fessurata.")
        rho_min = max(0.26 * 0.30 * cls.fck ** (2 / 3) / acc.fyk, 0.0013)   # 4.1.6.1.1
        if As < rho_min * b * dd:
            self.note.append(f"Armatura tesa inferiore al minimo di 4.1.6.1.1 ({rho_min * b * dd:.0f} mm2).")
        return self.verifiche
