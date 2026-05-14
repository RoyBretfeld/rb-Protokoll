# Requirements (PRD)
_Single Source of Truth für alle Features — SPEC-Phase Output_

---

## [RB-Police-Hardening]
**Status:** DONE
**Erstellt:** 2026-04-15
**Slice-Ref:** roadmap.md#slice-1

### Problem
Das Police-Gate (`rb check`) hat 5 zusammenhängende Bugs die verhindern, dass es seine Schutzfunktion erfüllt:
1. `check_system_facts()` wird nie von `rb check` aufgerufen — nur von `rb init`
2. Platzhalter in `02_SYSTEM_FACTS.md` erzeugen WARNING statt HARD-FAIL (Exit 1)
3. `BASELINE_TEST_CMD` und `FULL_TEST_CMD` sind als Literal-Platzhalter in `rb.py` eincompiliert, nicht aus SYSTEM_FACTS gelesen
4. `rb learn` zeigt auf externen absoluten Pfad statt auf `docs/_rb/03_ERROR_DB.md`
5. `pre_commit_police.py` hat keinen SYSTEM_FACTS-Existenz- oder Platzhalter-Check

### Akzeptanzkriterien
- [ ] `rb check` ruft SYSTEM_FACTS-Validierung auf und failt mit Exit 1 bei ungelösten Platzhaltern
- [ ] `check_system_facts()` gibt `False` zurück wenn Platzhalter gefunden werden (HARD-FAIL)
- [ ] `BASELINE_TEST_CMD` und `FULL_TEST_CMD` werden zur Laufzeit aus `02_SYSTEM_FACTS.md` gelesen
- [ ] `rb learn` verweist auf `docs/_rb/03_ERROR_DB.md` (relativ, portabel)
- [ ] `pre_commit_police.py` prüft Existenz und Platzhalter-Freiheit von `02_SYSTEM_FACTS.md`
- [ ] Alle Fixes bestehen den TAG-Guard (Zero-Mock, I/O-Clean, 5/5 Gesetze)
- [ ] `rb check` läuft erfolgreich durch wenn SYSTEM_FACTS befüllt ist
- [ ] `rb check` failt korrekt wenn SYSTEM_FACTS fehlt oder Platzhalter enthält

### Out-of-Scope
- Befüllen der Platzhalter in `02_SYSTEM_FACTS.md` (projektspezifisch, separater Task)
- Neubau der gesamten CLI-Architektur
- Hinzufügen neuer rb-Unterbefehle
- Änderungen am packer.py oder setup_hooks.py

### Technische Notizen
- SYSTEM_FACTS-Parsing: Regex `r'^\s*-\s*(?:Install|Start|Stop|Baseline|Full|Lint|Typecheck):\s*(.+)$'` liest Commands aus der Markdown-Liste
- Fallback-Verhalten: Wenn SYSTEM_FACTS-Datei fehlt → HARD-FAIL (kein Graceful-Degradation)
- `pre_commit_police.py` kann `check_system_facts()`-Logik duplizieren oder importieren — Import ist sauberer, erfordert aber dass rb.py als Package nutzbar ist. Einfacher: Police bekommt eigene `check_system_facts()`-Funktion.

---

<!-- Template für jeden neuen Eintrag:

## [Feature-Name]
**Status:** DRAFT | APPROVED | IN-PROGRESS | DONE
**Erstellt:** YYYY-MM-DD
**Slice-Ref:** roadmap.md#slice-N

### Problem
Was ist das Problem oder die Anforderung?

### Akzeptanzkriterien
- [ ] Kriterium 1
- [ ] Kriterium 2

### Out-of-Scope
Was wird explizit NICHT gebaut?

### Technische Notizen
Optionale Hinweise für PLAN-Phase.

-->
