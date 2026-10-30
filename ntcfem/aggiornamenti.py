"""Aggiornamento del programma dal repository GitHub.

Metodo semplice: la cartella del programma e' un clone git; all'avvio si
controlla se il ramo remoto ha commit nuovi e, con conferma, si fa `git pull`.
"""
import subprocess
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent


def _git(*args):
    return subprocess.run(["git", "-C", str(RADICE), *args], capture_output=True, text=True, timeout=60)


def controlla():
    """Restituisce il numero di aggiornamenti disponibili (0 se aggiornato, None se offline/non git)."""
    if not (RADICE / ".git").exists():
        return None
    if _git("fetch", "--quiet").returncode != 0:
        return None
    r = _git("rev-list", "--count", "HEAD..@{u}")
    return int(r.stdout.strip()) if r.returncode == 0 else None


def aggiorna():
    r = _git("pull", "--ff-only")
    return r.returncode == 0, (r.stdout + r.stderr).strip()
