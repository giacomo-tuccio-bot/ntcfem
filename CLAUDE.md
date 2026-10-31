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
- `ntcfem/server.py`  app WSGI unica (pagina + /api/calcola, /api/ottimizza), entrypoint Vercel in `pyproject.toml`
- `ntcfem/web.py`  funzioni chiamate dalle API; `web/index.html` pagina
- Account: Supabase Auth + tabella `progetti` (RLS, `supabase/migrations/`); il browser usa solo la chiave pubblica.
  Ogni nuova tabella deve avere RLS attiva e policy per `authenticated` con `(select auth.uid())`.
- `strumenti/server_locale.py`  stessa app in locale (porta 8000)
- Online le dipendenze sono solo quelle di `requirements.txt`: tenerle leggere

## Catalogo dei calcoli
- Elenco completo: `docs/catalogo_calcoli.txt`; stato e fasi: `dati/catalogo.json`
- Segui `docs/ROADMAP.md` per l'ordine di lavoro e le regole di ogni nuovo modulo
- Verifiche di sezione riusabili in `ntcfem/norme/`; nuovi elementi in `ntcfem/elementi/`

## Ottimizzazione (obiettivo principale del progetto)
- Il calcolo numerico lo fa il codice in `ntcfem/ottimizzazione/`; Claude sceglie le strategie,
  lancia le varianti, confronta e spiega. Mai proporre soluzioni non verificate dal codice.
- Cambiare una sezione cambia le sollecitazioni: rifare sempre l'analisi globale e riverificare.
- Obiettivo = costo totale (acciaio + cls + casseri + posa), non solo kg di ferro.
- Preferire soluzioni ripetitive in cantiere (pochi diametri, sezioni uguali per piano).
- Ogni proposta va approvata dal progettista.

## Prossimi passi
1. Spettro dai parametri del sito (reticolo NTC per lat/long, interpolazione TR)
2. Analisi dei carichi verticali e combinazioni SLU/SLE
3. Sollecitazioni nelle aste e verifiche c.a. (flessione, taglio, gerarchia delle resistenze)
4. Export carpenterie e armature in DXF (ezdxf)
5. Interfaccia grafica (FreeCAD o web)
