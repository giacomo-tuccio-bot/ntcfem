# Roadmap ntcfem

Obiettivo: coprire il catalogo in `docs/catalogo_calcoli.txt` (481 voci).
Avanzamento: `python strumenti/catalogo.py stato` (dati in `dati/catalogo.json`).

## Regola per ogni nuova voce
1. Un modulo in `ntcfem/elementi/` che eredita da `ElementoCalcolo` e si registra con
   `@registra("<id catalogo>")`.
2. Verifiche con riferimento al paragrafo NTC 2018 / Circolare 7/2019.
3. Almeno un test in `tests/` confrontato con un calcolo a mano o con Edilus.
4. Aggiornare lo stato in `dati/catalogo.json`: `fatto` dopo i test, `validato` dopo il
   confronto con Edilus su un caso reale.

## Fasi
| Fase | Contenuto | Voci |
|---|---|---|
| 1 | Nucleo: combinazioni (2.5.3), verifiche sezioni c.a. (flessione, pressoflessione, taglio, SLE), relazione di calcolo | trasversale (tabella cap. 19) |
| 2 | Elementi singoli piu' frequenti: travi, pilastri, solai, plinti, travi rovesce, balconi, scale, muri a mensola, cerchiature, travi in acciaio e legno | 131 |
| 3 | Edificio completo c.a.: carichi verticali nel modello 3D, statica lineare, regolarita', torsione accidentale, SLD, P-Delta, gerarchia delle resistenze, nodi | 25 |
| 4 | Edifici esistenti: rinforzi, FRP/FRCM, cambio d'uso, miglioramento/adeguamento | 40 |
| 5 | Acciaio, unioni, legno, elementi accessori | 97 |
| 6 | Muratura, geotecnica, pali, opere di sostegno, vasche, ascensori | 123 |
| 7 | Avanzate: pushover, time history, isolamento, incendio, vetro, cantiere | 65 |

In parallelo: export DXF (ezdxf), interfaccia grafica, spettro dal reticolo NTC.

## Stato del nucleo (fase 1)
- [x] Combinazioni SLU / SLE rara, frequente, quasi permanente
- [x] Flessione semplice sezione rettangolare a doppia armatura
- [x] Taglio senza e con staffe verticali
- [ ] Pressoflessione retta e deviata (domini N-M)
- [ ] Sezioni a T, circolari
- [ ] SLE: tensioni, fessurazione, freccia a sezione fessurata
- [ ] Combinazione sismica e dettagli costruttivi cap. 7
- [ ] Relazione di calcolo in PDF/DOCX
