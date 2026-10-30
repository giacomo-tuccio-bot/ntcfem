# ntcfem

Prototipo di software di calcolo strutturale per edifici in c.a. secondo NTC 2018,
con controllo dei risultati tramite Claude Code.

> Strumento in sviluppo, non validato: i risultati vanno confrontati con un software
> commerciale (es. Edilus). La responsabilita' del calcolo resta del progettista.

## Cosa fa oggi (v0.1.0)
- Telaio 3D con impalcati rigidi, masse G1+G2+psi2*Q
- Analisi modale (periodi, masse partecipanti)
- Spettro di progetto SLV NTC 2018 e combinazione CQC
- Taglio alla base, spostamenti e drift di piano
- Controllo con Claude Code (`--claude`)
- Aggiornamento automatico dal repository

## Installazione
```
git clone <indirizzo-del-repo> ntcfem
cd ntcfem
pip install -r requirements.txt
```
Per il controllo con Claude serve anche Claude Code installato e collegato al tuo account.

## Uso
```
python main.py esempi/telaio_prova.json            # calcolo
python main.py esempi/telaio_prova.json --claude   # calcolo + controllo di Claude
python main.py --aggiorna                          # aggiorna il programma
python -m pytest                                    # test di validazione
```
I risultati vanno nella cartella `output/` (JSON e testo).

## Formato del modello
Vedi `esempi/telaio_prova.json` (generato da `esempi/genera_telaio_prova.py`).
