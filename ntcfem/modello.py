"""Lettura del modello strutturale da file JSON.

Formato (vedi esempi/telaio_prova.json):
  nodi:      [{"id", "x", "y", "z", "incastro": bool}]
  sezioni:   {"nome": {"b", "h", "materiale"}}
  aste:      [{"id", "i", "j", "sezione", "tipo": "pilastro"|"trave"}]
  impalcati: [{"z", "G1", "G2", "Q", "psi2"}]   carichi in kN/m2
  sismica:   {"ag", "F0", "Tc_star", "sottosuolo", "topografia", "q"}
"""
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

DATI = Path(__file__).resolve().parent.parent / "dati"


def carica_dati(nome):
    return json.loads((DATI / nome).read_text(encoding="utf-8"))


@dataclass
class Materiale:
    nome: str
    E: float      # kN/m2
    G: float      # kN/m2
    peso: float   # kN/m3

    @classmethod
    def calcestruzzo(cls, nome):
        d = carica_dati("materiali.json")["calcestruzzo"][nome]
        fcm = d["fck"] + 8.0
        E = 22000 * (fcm / 10) ** 0.3 * 1e3
        return cls(nome, E, E / (2 * (1 + d["nu"])), d["peso"])


def proprieta_rettangolo(b, h):
    """A, I forte (b h^3/12), I debole, J torsionale (formula approssimata)."""
    A = b * h
    a, c = max(b, h), min(b, h)
    J = a * c**3 * (1 / 3 - 0.21 * (c / a) * (1 - c**4 / (12 * a**4)))
    return A, b * h**3 / 12, h * b**3 / 12, J


class Modello:
    def __init__(self, dati):
        self.dati = dati
        self.nodi = {n["id"]: n for n in dati["nodi"]}
        self.ids = [n["id"] for n in dati["nodi"]]
        self.indice = {nid: k for k, nid in enumerate(self.ids)}
        self.coord = np.array([[n["x"], n["y"], n["z"]] for n in dati["nodi"]], float)
        self.sezioni = dati["sezioni"]
        self.aste = dati["aste"]
        self.impalcati = sorted(dati["impalcati"], key=lambda d: d["z"])
        self.sismica = dati["sismica"]
        self.materiali = {s["materiale"]: Materiale.calcestruzzo(s["materiale"])
                          for s in self.sezioni.values()}

    @classmethod
    def da_file(cls, percorso):
        return cls(json.loads(Path(percorso).read_text(encoding="utf-8")))

    def lunghezza(self, asta):
        pi = self.coord[self.indice[asta["i"]]]
        pj = self.coord[self.indice[asta["j"]]]
        return float(np.linalg.norm(pj - pi))

    def livello(self, z, tol=1e-3):
        """Indice dell'impalcato alla quota z, oppure None."""
        for k, imp in enumerate(self.impalcati):
            if abs(imp["z"] - z) < tol:
                return k
        return None

    def nodi_impalcato(self, k):
        return [nid for nid in self.ids
                if abs(self.nodi[nid]["z"] - self.impalcati[k]["z"]) < 1e-3]

    def masse_impalcati(self, g=9.81):
        """Peso sismico (G1+G2+psi2*Q, peso proprio aste) e geometria di ogni impalcato.

        Travi: tutto il peso all'impalcato in cui stanno.
        Pilastri: meta' peso a ciascun estremo che cade su un impalcato.
        Solaio: area del rettangolo che racchiude i nodi dell'impalcato.
        """
        out = []
        for k, imp in enumerate(self.impalcati):
            xy = np.array([[self.nodi[n]["x"], self.nodi[n]["y"]] for n in self.nodi_impalcato(k)])
            (x0, y0), (x1, y1) = xy.min(0), xy.max(0)
            Lx, Ly = x1 - x0, y1 - y0
            W_solaio = Lx * Ly * (imp["G1"] + imp["G2"] + imp["psi2"] * imp["Q"])
            out.append(dict(z=imp["z"], Lx=Lx, Ly=Ly, xg=(x0 + x1) / 2, yg=(y0 + y1) / 2,
                            W_solaio=W_solaio, W_aste=0.0))
        for a in self.aste:
            s = self.sezioni[a["sezione"]]
            w = s["b"] * s["h"] * self.materiali[s["materiale"]].peso * self.lunghezza(a)
            zi, zj = self.nodi[a["i"]]["z"], self.nodi[a["j"]]["z"]
            if a["tipo"] == "trave":
                k = self.livello(zi)
                if k is not None:
                    out[k]["W_aste"] += w
            else:
                for z in (zi, zj):
                    k = self.livello(z)
                    if k is not None:
                        out[k]["W_aste"] += w / 2
        for d in out:
            d["W"] = d["W_solaio"] + d["W_aste"]
            d["m"] = d["W"] / g
            d["Jp"] = d["m"] * (d["Lx"] ** 2 + d["Ly"] ** 2) / 12
        return out
