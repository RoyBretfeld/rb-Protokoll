# Tech-Debt & Concerns: RB-GSD Protokoll Framework
_Updated: 2026-04-15_

## CRITICAL

### C1 — `rb check` prüft SYSTEM_FACTS nicht
- `check_system_facts()` wird nur von `rb init` aufgerufen, nicht von `rb check`.
- Police (`pre_commit_police.py`) hat keinen SYSTEM_FACTS-Check.
- **Risiko:** Commits durchs Gate, obwohl System-Fakten unvollständig → MAP/SPEC auf Sand gebaut.

### C2 — Platzhalter erzeugen WARNING statt HARD-FAIL
- `check_system_facts()` findet `{{PLACEHOLDER}}` aber gibt `True` zurück.
- Protokoll fordert: ungelöste Platzhalter = sofortiger Stopp.
- **Risiko:** Agent arbeitet weiter mit unvollständiger Basis.

## HIGH

### H1 — Commands als Template-Platzhalter eincompiliert
- `rb.py:94` und `rb.py:108` enthalten Literal-Strings `"{{BASELINE_TEST_CMD}}"` bzw. `"{{FULL_TEST_CMD}}"`.
- Nicht aus `02_SYSTEM_FACTS.md` gelesen → Commands nie funktional.
- **Risiko:** `rb test` und `rb check` (Baseline-Teil) können nicht arbeiten.

### H2 — `rb learn` zeigt auf externen absoluten Pfad
- `rb.py:116`: `Path(r"E:\...\03_ERROR_DB.md")` — extern, nicht portabel.
- SSOT-Regel: Error-DB liegt bei `docs/_rb/03_ERROR_DB.md`.
- **Risiko:** Pfad existiert nur auf diesem Rechner; CI/andere Agenten scheitern.

## LOW

### L1 — Duplizierte SECRET_PATTERNS-Kommentare
- `pre_commit_police.py:24-25`: Zeile `# Patterns causing immediate failure if found in code` steht zweimal.

### L2 — Kein Typecheck auf Windows-Pfade
- `pre_commit_police.py` nutzt `Path.rglob()` — funktioniert, aber Pfad-Vergleiche in `check_migration_consistency()` nutzen manuelles `replace("\\", "/")`.
