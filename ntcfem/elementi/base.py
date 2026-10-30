"""Struttura comune a tutti i moduli di calcolo degli elementi.

Ogni elemento ha: dati di input (dict), calcola() -> lista di Verifica, relazione() -> testo.
"""
from dataclasses import asdict, dataclass

REGISTRO = {}


def registra(*id_catalogo):
    def deco(cls):
        cls.id_catalogo = id_catalogo
        REGISTRO[cls.__name__] = cls
        return cls
    return deco


@dataclass
class Verifica:
    nome: str
    domanda: float          # sollecitazione di progetto (Ed)
    capacita: float         # resistenza di progetto (Rd)
    unita: str
    riferimento_ntc: str
    combinazione: str = ""

    @property
    def rapporto(self):
        return abs(self.domanda) / self.capacita if self.capacita else float("inf")

    @property
    def esito(self):
        return "OK" if self.rapporto <= 1.0 else "NON VERIFICATA"

    def dict(self):
        return asdict(self) | {"rapporto": round(self.rapporto, 3), "esito": self.esito}


class ElementoCalcolo:
    titolo = "Elemento"
    id_catalogo = ()

    def __init__(self, dati: dict):
        self.dati = dati
        self.verifiche: list[Verifica] = []
        self.note: list[str] = []
        self.valori: dict = {}

    def calcola(self) -> list[Verifica]:
        raise NotImplementedError

    def risultati(self):
        if not self.verifiche:
            self.calcola()
        return {"elemento": self.titolo, "id_catalogo": list(self.id_catalogo), "dati": self.dati,
                "valori": self.valori, "verifiche": [v.dict() for v in self.verifiche],
                "esito_globale": "OK" if all(v.esito == "OK" for v in self.verifiche) else "NON VERIFICATO",
                "note": self.note}

    def relazione(self):
        r = self.risultati()
        L = [r["elemento"].upper(), "-" * 70, "Dati:"]
        L += [f"  {k} = {v}" for k, v in self.dati.items()]
        L += ["Valori calcolati:"] + [f"  {k} = {v}" for k, v in self.valori.items()]
        L += ["", f"{'Verifica':34s} {'Ed':>9} {'Rd':>9} {'Ed/Rd':>6}  Esito"]
        for v in self.verifiche:
            L.append(f"{v.nome:34s} {v.domanda:9.2f} {v.capacita:9.2f} {v.rapporto:6.2f}  {v.esito}"
                     f"   [{v.unita}, NTC {v.riferimento_ntc}]")
        L += ["", f"ESITO: {r['esito_globale']}"] + [f"Nota: {n}" for n in self.note]
        return "\n".join(L)
