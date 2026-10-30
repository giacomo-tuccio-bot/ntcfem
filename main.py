"""Uso:
    python main.py esempi/telaio_prova.json            calcolo
    python main.py esempi/telaio_prova.json --claude   calcolo + controllo con Claude Code
    python main.py --aggiorna                          scarica l'ultima versione dal repo
"""
import argparse
import json
from pathlib import Path

from ntcfem import __version__, aggiornamenti
from ntcfem.calcolo import come_testo, esegui, salva
from ntcfem.modello import Modello


def main():
    ap = argparse.ArgumentParser(description=f"ntcfem v{__version__}")
    ap.add_argument("modello", nargs="?")
    ap.add_argument("--claude", action="store_true", help="controllo dei risultati con Claude Code")
    ap.add_argument("--aggiorna", action="store_true", help="aggiorna il programma dal repository")
    ap.add_argument("--no-check", action="store_true", help="non controllare gli aggiornamenti")
    a = ap.parse_args()

    if a.aggiorna:
        ok, msg = aggiornamenti.aggiorna()
        print(msg)
        return
    if not a.no_check:
        n = aggiornamenti.controlla()
        if n:
            print(f"*** Sono disponibili {n} aggiornamenti: esegui  python main.py --aggiorna ***\n")
    if not a.modello:
        ap.print_help()
        return

    mod = Modello.da_file(a.modello)
    r = esegui(mod)
    print(come_testo(r))
    out = salva(r, "output", Path(a.modello).stem)
    print(f"\nRisultati salvati in {out}")

    if a.claude:
        from ntcfem.claude_bridge import analizza
        print("\nControllo con Claude in corso...")
        s = analizza(a.modello, out)
        Path(out).with_name(Path(a.modello).stem + "_claude.json").write_text(
            json.dumps(s, indent=2, ensure_ascii=False), encoding="utf-8")
        for av in s.get("avvisi", []):
            print(f"[{av['livello'].upper()}] {av['messaggio']} ({av.get('riferimento_ntc', '')})")
        for p in s.get("proposte", []):
            print(f"[PROPOSTA] {p['elemento']}: {p['modifica']} - {p['motivo']}")


if __name__ == "__main__":
    main()
