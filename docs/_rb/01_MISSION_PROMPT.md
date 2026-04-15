# 01_MISSION_PROMPT (RB-GSD Boot-Sektor)
**Version:** 3.0 — MAR-Integration (Multi-Agent-Review)
**Status:** Active — Normatives Dokument

---

## Zweck

Dieser Prompt ist der **Boot-Sektor** für jeden Agenten, der dieses Projekt öffnet.
Jede KI muss dieses Dokument zuerst lesen und sich danach verhalten.

---

## Mission

Du arbeitest nach dem **RB-GSD Protokoll**. Deine Aufgabe ist industrielles AI Engineering:
minimal, prüfbar, sicher, in atomaren Schritten.

---

## GSD-PHASEN-LOGIK (Zwingend)

Jede Arbeit — ob neues Feature oder Legacy-Fix — folgt diesem Ablauf:

### PHASE 1: MAP
> *"Was existiert?"*

- **Trigger:** Vor jeder Änderung an bestehendem Code.
- **Output:** `.planning/codebase/architecture.md` + `.planning/codebase/concerns.md`
- **Regel:** Ohne MAP kein SPEC. Code anfassen ohne Karte ist verboten.

### PHASE 2: SPEC
> *"Was wird gebraucht?"*

- **Trigger:** Bei jeder neuen Funktion oder jedem Bug-Fix.
- **Output:** Eintrag in `.planning/requirements.md` (PRD-Format)
- **Format:**
  ```
  ## [Feature-Name]
  - Problem: ...
  - Akzeptanzkriterien: ...
  - Out-of-Scope: ...
  ```
- **Stopp:** Nach SPEC wartet der Agent auf `/approve` vom User.

### PHASE 3: PLAN
> *"Wie wird es gebaut?"*

- **Trigger:** Nach User-Freigabe des SPEC.
- **Output:** Atomare Slices in `.planning/roadmap.md`
- **Boundary Map pro Slice:**
  ```
  Slice N: [Name]
  - Braucht: [Abhängigkeiten]
  - Liefert: [Output]
  - Testkriterium: [Wie verifiziert?]
  ```
- **Stopp:** Nach PLAN nochmals warten auf explizites `USER_APPROVE: EXECUTE`.

### PHASE 4: EXEC — Builder-Rolle
> *"Bauen."*

- **Trigger:** Nach `USER_APPROVE: EXECUTE`
- **Regel:** Pro Slice ein Git-Commit. Kein Slice überspringen.
- **Autonomie:** Maximale Autonomie gemäß §5 (`01_PLAN_EXECUTION.md`).
- **Zero-Mock-Policy:** §5 REALD-Protokoll gilt absolut. Kein Commit mit Mock-Daten.
- **Nach jedem Slice:** Weiter zu PHASE 4b (TAG) — KEIN direktes Commit.

---

### PHASE 4b: TAG — Triple-Agent-Guard (Mechanische Prüfkette)
> *«Der Builder darf sich nicht selbst freigeben. Der Critic hasst den Builder. Das ist gewollt.»*

Nach Fertigstellung eines Slices läuft zwingend der TAG-Workflow.
**Kein manuelles Durchwinken.** Der Checker entscheidet — nicht der Agent.

#### Ausführen (Pflicht vor jedem Commit):
```powershell
python scripts/rb_tag_check.py --all --slice "Slice-N: Name"
```

#### Bei CRITIC PASS → Sentinel-Bestätigung (manuell):
Checke die 5 Gesetze (Details: `docs/_rb/00_BOOT_PROTOCOL.md`). Dann:
```powershell
git commit -m "[SLICE-N] Beschreibung

TAG-GUARD:
  BUILDER:  ✅ I/O-Clean, Zero-Mock
  CRITIC:   ✅ Mock-Scan CLEAN | Typecheck CLEAN
  SENTINEL: ✅ SENTINEL-OK (5/5 Gesetze)"
```

#### Bei CRITIC HARD-FAIL:
```
❌ STOPP — Kein Korrekturversuch.
→ Zurück zu PHASE 3 (PLAN). Slice neu definieren.
→ SPEC mit User re-validieren (§4 Menschliche Hoheit).
→ Erst dann neuer Builder-Versuch.
```

> Vollständige Rollendefinitionen: `docs/_rb/00_BOOT_PROTOCOL.md`


### PHASE 5: VERIFY
> *"Stimmt das Ergebnis?"*

- **Trigger:** Nach EXEC des letzten Slice.
- **Output:** Eintrag in `.planning/roadmap.md` unter `## VERIFY` mit Status.
- **Format:**
  ```
  ## VERIFY — [Feature-Name]
  - Datum: YYYY-MM-DD
  - Getestete Kriterien: [Liste aus SPEC]
  - Status: ✅ DONE / ❌ FAILED
  - Abweichungen: ...
  ```
- **Blockade:** Kein Merge ohne dokumentiertes VERIFY (Police-Sentinel-Rule).

---

## SSOT-Regel

Das Gedächtnis lebt in `.planning/` — nicht im Chat.

| Artefakt | Pfad |
|---|---|
| Architektur-Map | `.planning/codebase/architecture.md` |
| Tech-Debts | `.planning/codebase/concerns.md` |
| PRD / Anforderungen | `.planning/requirements.md` |
| Slices & Boundary Maps | `.planning/roadmap.md` |

---

## Siehe auch

- [§5 Plan Execution Autonomy](01_PLAN_EXECUTION.md)
- [System Facts / Stack](02_SYSTEM_FACTS.md)
- [Security Rules](05_SECURITY.md)
- [TAG-Check Script](scripts/rb_tag_check.py)
- [Pre-Commit Police](scripts/pre_commit_police.py)
