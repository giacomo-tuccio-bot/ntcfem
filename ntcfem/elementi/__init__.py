"""Moduli di calcolo dei singoli elementi.

Ogni modulo definisce una classe che eredita da ElementoCalcolo e la registra con
@registra("id_catalogo", ...). Gli id corrispondono a dati/catalogo.json.
"""
from .base import REGISTRO, ElementoCalcolo, Verifica, registra  # noqa: F401
from .trave_ca_appoggiata import TraveCaAppoggiata  # noqa: F401
