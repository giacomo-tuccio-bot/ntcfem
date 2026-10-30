"""Collegamento con Claude Code (modalita' non interattiva `claude -p`).

Claude legge il modello e i risultati e restituisce SOLO suggerimenti in JSON.
Nessuna modifica viene applicata al modello senza conferma del progettista.
"""
import json
import shutil
import subprocess
from pathlib import Path

PROMPT = """Sei un assistente per il controllo di un calcolo strutturale secondo NTC 2018.
Leggi il modello {modello} e i risultati {risultati}.
Controlla: coerenza del modello, masse partecipanti (>=85%), regolarita', periodi,
taglio alla base, spostamenti e drift. Proponi ottimizzazioni (sezioni, disposizione).
Non modificare nessun file. Rispondi SOLO con JSON in questo formato:
{{"avvisi": [{{"livello": "errore|attenzione|info", "messaggio": "...", "riferimento_ntc": "..."}}],
  "proposte": [{{"elemento": "...", "modifica": "...", "motivo": "..."}}]}}"""


def analizza(modello, risultati, timeout=600):
    if shutil.which("claude") is None:
        raise RuntimeError("Claude Code non trovato: installalo e accedi con il tuo account.")
    prompt = PROMPT.format(modello=Path(modello).as_posix(), risultati=Path(risultati).as_posix())
    r = subprocess.run(["claude", "-p", prompt, "--allowedTools", "Read", "--output-format", "json"],
                       capture_output=True, text=True, timeout=timeout)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip() or "Errore da Claude Code")
    testo = json.loads(r.stdout)["result"]
    inizio, fine = testo.find("{"), testo.rfind("}")
    return json.loads(testo[inizio:fine + 1])
