# Changelog

## 0.3.0 - 2026-10-31
- Ottimizzazione armature longitudinali a peso minimo (ntcfem/ottimizzazione/armature.py)
- Confronto sezioni alternative a costo minimo con prezzario modificabile (ottimizzazione/sezioni.py)
- Vincoli: MRd >= MEd, As min/max (4.1.6.1.1), interferro, x/d <= 0.45

## 0.2.0 - 2026-10-30
- Catalogo dei 481 calcoli in dati/catalogo.json con fasi e stato (strumenti/catalogo.py)
- Nucleo norme: combinazioni NTC 2.5.3, flessione e taglio sezioni c.a. (4.1.2.3)
- Struttura modulare degli elementi (ntcfem/elementi) e primo modulo: trave c.a. appoggiata
- docs/ROADMAP.md

## 0.1.0 - 2026-10-30
- Prima versione: telaio 3D, impalcati rigidi, analisi modale, spettro SLV NTC 2018, CQC
- Modello e dati normativi in JSON
- Collegamento a Claude Code e aggiornamento da GitHub
