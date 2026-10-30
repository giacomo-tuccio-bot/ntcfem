"""Verifiche di sezioni in cemento armato - NTC 2018 par. 4.1.

Unita': N, mm, MPa (momenti in N*mm). Le funzioni di alto livello convertono in kN e kNm.
"""
from dataclasses import dataclass
from math import sqrt

from ..modello import carica_dati

_C = carica_dati("ntc2018.json")["ca"]
_M = carica_dati("materiali.json")


@dataclass
class Cls:
    fck: float

    @classmethod
    def da_classe(cls, nome):
        return cls(_M["calcestruzzo"][nome]["fck"])

    @property
    def fcd(self):          # 4.1.2.1.1.1  fcd = acc fck / gc
        return _C["alfa_cc"] * self.fck / _C["gamma_c"]


@dataclass
class Acciaio:
    fyk: float = 450.0

    @property
    def fyd(self):          # 4.1.2.1.1.3  fyd = fyk / gs
        return self.fyk / _C["gamma_s"]

    @property
    def Es(self):
        return _C["Es_MPa"]


def area_barre(n, diam):
    return n * 3.141592653589793 * diam**2 / 4


def momento_resistente(b, h, c, As, As2, cls: Cls, acc: Acciaio):
    """MRd a flessione semplice di sezione rettangolare a doppia armatura (4.1.2.3.4.2).

    Diagramma rettangolare del cls (stress-block 0.8x, tensione fcd, 4.1.2.1.2.1),
    eps_cu = 0.35%, acciaio elastico-perfettamente plastico. b, h, c in mm; As, As2 in mm2.
    Restituisce (MRd [kNm], x [mm], x/d).
    """
    d, d2 = h - c, c
    ecu, Es, fyd, fcd = _C["eps_cu"], acc.Es, acc.fyd, cls.fcd

    def sigma(eps):
        return max(-fyd, min(fyd, Es * eps))

    def squilibrio(x):
        Cc = 0.8 * x * b * fcd
        Cs = As2 * sigma(ecu * (x - d2) / x)
        Ts = As * sigma(ecu * (d - x) / x)
        return Cc + Cs - Ts

    lo, hi = 1e-3, h
    for _ in range(200):                 # bisezione sull'asse neutro
        x = (lo + hi) / 2
        if squilibrio(x) > 0:
            hi = x
        else:
            lo = x
    Cc = 0.8 * x * b * fcd
    Cs = As2 * sigma(ecu * (x - d2) / x)
    M = Cc * (d - 0.4 * x) + Cs * (d - d2)
    return M / 1e6, x, x / d


def taglio_senza_staffe(b, d, As, cls: Cls, sigma_cp=0.0):
    """VRd per elementi senza armatura a taglio (4.1.2.3.5.1, eq. 4.1.23). Restituisce kN."""
    k = min(1 + sqrt(200 / d), 2.0)
    rho = min(As / (b * d), 0.02)
    vmin = 0.035 * k**1.5 * sqrt(cls.fck)
    v1 = 0.18 * k * (100 * rho * cls.fck) ** (1 / 3) / _C["gamma_c"] + 0.15 * sigma_cp
    return max(v1, vmin + 0.15 * sigma_cp) * b * d / 1e3


def taglio_con_staffe(b, d, Asw, s, cls: Cls, acc: Acciaio, alfa_c=1.0):
    """VRd con staffe verticali (4.1.2.3.5.2, eq. 4.1.27-4.1.29), 1 <= cot(theta) <= 2.5.

    Asw = area di un'intera staffa (tutti i bracci) [mm2], s = passo [mm].
    Restituisce (VRd [kN], VRsd, VRcd, cot_theta).
    """
    fcd1 = 0.5 * cls.fcd                                   # nu*fcd con nu = 0.5
    def vrsd(ct):
        return 0.9 * d * Asw / s * acc.fyd * ct
    def vrcd(ct):
        return 0.9 * d * b * alfa_c * fcd1 * ct / (1 + ct**2)
    migliore = max((min(vrsd(ct), vrcd(ct)), ct) for ct in [1 + i * 0.001 for i in range(1501)])
    ct = migliore[1]
    return migliore[0] / 1e3, vrsd(ct) / 1e3, vrcd(ct) / 1e3, ct
