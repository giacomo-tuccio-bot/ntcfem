# Istruzioni per Claude Code - progetto ntcfem

Software di calcolo strutturale per edifici in c.a. secondo NTC 2018 (D.M. 17/01/2018)
e Circolare n. 7/2019. Prototipo: i risultati vanno sempre confrontati con Edilus.

## Regole
- Lingua: italiano per codice (nomi), commenti, messaggi e documentazione.
- Ogni formula normativa deve citare il paragrafo NTC nel commento.
- I dati normativi (tabelle, materiali) stanno in `dati/*.json`, non nel codice.
- Prima di ogni commit: `python -m pytest` (o `python tests/test_solutore.py`) deve passare.
- Se un valore del test di regressione cambia, spiegare perche' nel messaggio di commit.
- Ad ogni rilascio aggiornare `VERSION` e `CHANGELOG.md`.

## Quando analizzi un calcolo (bottone "Analizza con Claude")
- Non modificare mai il modello: proponi, il progettista decide.
- Segnala sempre il riferimento NTC di ogni avviso.
- La responsabilita' del calcolo resta del progettista (NTC cap. 10).

## Struttura
- `ntcfem/modello.py`   lettura modello JSON, materiali, masse di impalcato
- `ntcfem/solutore.py`  telaio 3D, impalcati rigidi, analisi modale
- `ntcfem/sismica.py`   spettro NTC 2018 par. 3.2.3, CQC
- `ntcfem/calcolo.py`   esecuzione completa e output
- `ntcfem/claude_bridge.py`  chiamata a `claude -p`
- `ntcfem/aggiornamenti.py`  aggiornamento da GitHub (git pull)

## Prossimi passi
1. Spettro dai parametri del sito (reticolo NTC per lat/long, interpolazione TR)
2. Analisi dei carichi verticali e combinazioni SLU/SLE
3. Sollecitazioni nelle aste e verifiche c.a. (flessione, taglio, gerarchia delle resistenze)
4. Export carpenterie e armature in DXF (ezdxf)
5. Interfaccia grafica (FreeCAD o web)
