# Roadmap — Slices & Boundary Maps
_PLAN-Phase Output — Single Source of Truth für Ausführungsreihenfolge_

---

## Aktiver Sprint

### Slice 1: check_system_facts HARD-FAIL + rb check-Integration
**Status:** DONE
**Spec-Ref:** requirements.md#rb-police-hardening

| | |
|---|---|
| **Braucht** | Keine Abhängigkeiten |
| **Liefert** | `check_system_facts()` gibt `False` bei Platzhaltern; `rb check` ruft die Funktion auf und failt mit Exit 1 |
| **Testkriterium** | 1. `rb check` mit Platzhalter-SYSTEM_FACTS → Exit 1 + HARD-FAIL-Meldung 2. `rb init` mit Platzhalter-SYSTEM_FACTS → Exit 1 (nicht mehr nur WARNING) |
| **Fehlerbehandlung** | Wenn SYSTEM_FACTS fehlt → Exit 1 mit klarer Meldung (bestehend); wenn Datei vorhanden aber nicht lesbar → Exit 1 mit IO-Error |

**Commit-Message:** `[SLICE-1] rb check: HARD-FAIL on SYSTEM_FACTS placeholders`

---

### Slice 2: Commands zur Laufzeit aus SYSTEM_FACTS lesen
**Status:** DONE
**Spec-Ref:** requirements.md#rb-police-hardening

| | |
|---|---|
| **Braucht** | Slice 1 (SYSTEM_FACTS-Parsing-Infrastruktur) |
| **Liefert** | `BASELINE_TEST_CMD` und `FULL_TEST_CMD` werden zur Laufzeit aus `02_SYSTEM_FACTS.md` gelesen; keine Template-Platzhalter mehr im Code |
| **Testkriterium** | 1. `rb check` liest Baseline-Command aus SYSTEM_FACTS und führt ihn aus 2. `rb test` liest Full-Test-Command aus SYSTEM_FACTS 3. Wenn Command-Feld leer oder Platzhalter → Warnung + Skip (nicht FAIL, da Commands optional) |
| **Fehlerbehandlung** | Wenn SYSTEM_FACTS nicht parsebar → Fallback auf bestehendes Verhalten + Warnung; wenn Command-Feld fehlt → Warnung + Skip |

**Commit-Message:** `[SLICE-2] rb: parse commands from SYSTEM_FACTS at runtime`

---

### Slice 3: rb learn Error-DB-Pfad korrigieren
**Status:** DONE
**Spec-Ref:** requirements.md#rb-police-hardening

| | |
|---|---|
| **Braucht** | Keine Abhängigkeiten |
| **Liefert** | `rb learn` verweist auf `docs/_rb/03_ERROR_DB.md` (relativ, portabel) |
| **Testkriterium** | 1. `rb learn` zeigt Pfad zu `docs/_rb/03_ERROR_DB.md` 2. Pfad funktioniert unabhängig von Rechner/CI-Umgebung |
| **Fehlerbehandlung** | Wenn Error-DB-Datei fehlt → Exit 1 mit Meldung (bestehend); Pfad bleibt relativ |

**Commit-Message:** `[SLICE-3] rb learn: fix Error-DB path to docs/_rb/03_ERROR_DB.md`

---

### Slice 4: pre_commit_police SYSTEM_FACTS-Check
**Status:** DONE
**Spec-Ref:** requirements.md#rb-police-hardening

| | |
|---|---|
| **Braucht** | Keine Abhängigkeiten |
| **Liefert** | `pre_commit_police.py` prüft Existenz und Platzhalter-Freiheit von `02_SYSTEM_FACTS.md`; FAIL bei fehlender Datei oder ungelösten Platzhaltern |
| **Testkriterium** | 1. Police läuft durch wenn SYSTEM_FACTS existiert und keine Platzhalter hat 2. Police failt wenn SYSTEM_FACTS fehlt 3. Police failt wenn SYSTEM_FACTS Platzhalter enthält 4. Fehlermeldung benennt die betroffenen Platzhalter |
| **Fehlerbehandlung** | Wenn Datei fehlt → FAIL mit "SYSTEM_FACTS missing"; wenn Platzhalter → FAIL mit Liste der ungelösten Felder |

**Commit-Message:** `[SLICE-4] police: add SYSTEM_FACTS existence and placeholder check`

---

## VERIFY

## VERIFY — RB-Police-Hardening
- Datum: 2026-04-15
- Getestete Kriterien:
  - [x] `rb check` ruft SYSTEM_FACTS-Validierung auf und failt mit Exit 1 bei ungelösten Platzhaltern
  - [x] `check_system_facts()` gibt `False` zurück wenn Platzhalter gefunden werden (HARD-FAIL)
  - [x] `BASELINE_TEST_CMD` und `FULL_TEST_CMD` werden zur Laufzeit aus `02_SYSTEM_FACTS.md` gelesen
  - [x] `rb learn` verweist auf `docs/_rb/03_ERROR_DB.md` (relativ, portabel)
  - [x] `pre_commit_police.py` prüft Existenz und Platzhalter-Freiheit von `02_SYSTEM_FACTS.md`
  - [x] Alle Fixes bestehen den TAG-Guard
  - [x] `rb check` failt korrekt wenn SYSTEM_FACTS Platzhalter enthält
  - [x] Police failt korrekt wenn SYSTEM_FACTS Platzhalter enthält
- Status: ✅ DONE
- Abweichungen: Keine funktionellen Abweichungen. Bekanntes Vorab-Problem: Windows cp1252-Encoding blockiert Emoji-Ausgabe ohne PYTHONIOENCODING=utf-8 (nicht Teil dieses SPEC).
