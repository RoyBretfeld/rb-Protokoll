# Architecture Map: RB-GSD Protokoll Framework
_Updated: 2026-04-15_

## Stack
- **Language:** Python 3.12
- **Dependencies:** Keine externen (nur stdlib: argparse, subprocess, re, pathlib)
- **Platform:** Windows 11 (Pfade mit `\\`, Shell: bash)

## Einstiegspunkte
- `scripts/rb.py` — CLI-Interface (check, test, pack, learn, init)
- `scripts/pre_commit_police.py` — Pre-Commit-Gate (Secrets, Blockfiles, Migration, VERIFY)
- `scripts/packer.py` — Kontext-Dump-Generator
- `scripts/setup_hooks.py` — Git-Hook-Installation

## rb.py — Kommando-Fluss

```
rb check → pre_commit_police.py → baseline tests (falls konfiguriert)
rb test  → FULL_TEST_CMD (aktuell Template-Platzhalter)
rb pack  → packer.py
rb learn → Error-DB Eintrag (Pfad: aktuell extern/inkorrekt)
rb init  → check_system_facts() (nur hier aufgerufen)
```

## pre_commit_police.py — Prüfreihenfolge

```
1. get_staged_files() → Git staged oder Full-Scan
2. check_verify_phase() → SENTINEL: SPEC ohne VERIFY blockiert
3. Blockfile-Scan → Forbidden filenames
4. Content-Scan → SECRET_PATTERNS auf scannable Dateien
5. Migration-Konsistenz → Schema + Migration prüfen
```

## SYSTEM_FACTS-Anbindung
- `docs/_rb/02_SYSTEM_FACTS.md` — SSOT für Stack, Pfade, Commands
- `check_system_facts()` in rb.py liest die Datei, aber:
  - Nur von `rb init` aufgerufen
  - Platzhalter erzeugen WARNING, nicht FAIL
  - Commands (BASELINE_TEST_CMD etc.) nicht aus SYSTEM_FACTS gelesen

## Ausgabe
- CLI-Output auf stdout/stderr
- Exit-Codes: 0 = OK, 1 = FAIL, 130 = Interrupt
