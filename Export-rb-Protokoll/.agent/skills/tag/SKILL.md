---
name: Triple-Agent-Guard (TAG)
description: Mechanische 3-Rollen-Prüfkette vor jedem Commit. Builder → Critic → Sentinel. Ersetzt freie Autonomie durch erzwungene Gewaltenteilung. Hard-Fail bei Mock/Type-Error.
author: Antigravity Core
version: 1.0.0
triggers:
  - "vor commit"
  - "TAG"
  - "triple agent"
  - "critic check"
---

# Triple-Agent-Guard (TAG) — v1.0

> **Kernprinzip:** Der Builder darf sich nicht selbst freigeben.
> Kein Slice landet in der Codebase ohne Critic-PASS und Sentinel-OK.

---

## DIE 3 ROLLEN

### 🔨 BUILDER-ROLE (Implementierung)

**Mandat:** Slice laut `roadmap.md` implementieren.

**Absolute Verbote:**
- ❌ Kein `mock`, `dummy`, `placeholder`, `fake`, `example_data`
- ❌ Kein `MagicMock()`, `Mock()`, `unittest.mock`
- ❌ Kein `// TODO`, `pass # TODO`, `raise NotImplementedError`
- ❌ Keine statischen Fallback-Objekte (`return {}`, `return []` ohne echten Grund)
- ❌ Kein Code ohne Pfad zu echtem I/O (DB, API, FS, Env)

**I/O-Zwang:** Jede Funktion, die Daten liefert, muss einen realen Datenpfad haben:
```python
# ❌ VERBOTEN (Builder-Verstoß):
def get_users() -> list:
    return [{"id": 1, "name": "Test"}]  # statisches Objekt

# ✅ ERLAUBT:
def get_users() -> list:
    return real_or_die(db.query("SELECT * FROM users"), "users")
```

**Output:** Fertiggestellter Code. Dann SOFORT weiter zu CRITIC — kein Commit.

---

### 🔍 CRITIC-ROLE (Härtung)

**Mandat:** Den Builder-Code aktiv zu zerstören versuchen. Fehler finden ist Erfolg.

**Der Critic hasst den Builder. Das ist gewollt.**

**Check 1 — Mock-Scan (Pflicht):**
```powershell
python .agent/skills/rb_police/scripts/rb_tag_check.py --mock-scan
```
Sucht nach: `mock`, `placeholder`, `example`, `temp`, `dummy`, `MagicMock`, `TODO`, `NotImplementedError`, `{{`, `pass #`

**Check 2 — Typecheck (wenn konfiguriert in SYSTEM_FACTS):**
```powershell
# Python:
mypy src/ --strict

# Node/TypeScript:
pnpm typecheck   # oder: npx tsc --noEmit
```

**Check 3 — Hard-Fail Runtime:**
```powershell
python .agent/skills/rb_police/scripts/rb_tag_check.py --hard-fail
```
Verifiziert dass `real_or_die()` / `env_or_die()` korrekt eingebunden sind.

**CRITIC-ERGEBNIS:**
```
[CRITIC] ✅ PASS — Alle Checks grün. Übergabe an SENTINEL.
   ODER
[CRITIC] ❌ HARD-FAIL — [Beschreibung des Verstoßes]
         → KEIN Korrekturversuch ohne neue SPEC-Validierung.
         → Builder muss zurück zu PLAN.
```

> **Regel:** Bei HARD-FAIL ist Korrigieren verboten.
> Der Fehler zeigt eine Lücke im PLAN, nicht nur im Code.
> → Zurück zu PHASE 3 (PLAN), SPEC neu validieren, dann neu bauen.

---

### 🛡️ SENTINEL-ROLE (Governance)

**Mandat:** Protokoll-Konformität bestätigen. Einzige Rolle die committen darf.

**Check — Die 5 Gesetze:**

| Gesetz | Frage | Status |
|---|---|---|
| §1 Transparenz | Hat jeder Prozess >500ms Feedback? | ✅/❌ |
| §2 Revidierbarkeit | Ist jede Aktion rückgängig machbar? | ✅/❌ |
| §3 Progressive Offenlegung | Ist die UI clean, Details per Klick? | ✅/❌ |
| §4 Menschliche Hoheit | Bestätigt der Mensch kritische Aktionen? | ✅/❌ |
| §5 REALD-Protokoll | Sind alle Daten real, kein Mock? | ✅/❌ |

**SENTINEL-ERGEBNIS:**
```
[SENTINEL] ✅ SENTINEL-OK — Protokoll-konform. Commit erlaubt.
    ODER
[SENTINEL] ❌ SENTINEL-BLOCK — §X verletzt: [Beschreibung]
           → Commit gesperrt bis Gesetz eingehalten.
```

---

## PFLICHT-PROTOKOLL (Commit-Log)

**Vor JEDEM `git commit` muss der Agent diesen Dialog intern protokollieren und ausgeben:**

```
╔══════════════════════════════════════════════════════════╗
║              TAG — TRIPLE-AGENT-GUARD                    ║
║              Slice: [N] — [Slice-Name]                   ║
╠══════════════════════════════════════════════════════════╣
║ BUILDER:  Code fertiggestellt. I/O-Pfad vorhanden.       ║
║           Kein Mock, kein TODO, kein statischer Fallback. ║
╠══════════════════════════════════════════════════════════╣
║ CRITIC:   Mock-Scan:    ✅ CLEAN                         ║
║           Typecheck:    ✅ CLEAN / ⚠️ N/A (nicht konfiguriert) ║
║           Hard-Fail:    ✅ CLEAN                         ║
║           → CRITIC: ✅ PASS                              ║
╠══════════════════════════════════════════════════════════╣
║ SENTINEL: §1 Transparenz:      ✅                        ║
║           §2 Revidierbarkeit:  ✅                        ║
║           §3 Offenlegung:      ✅                        ║
║           §4 Menschl. Hoheit:  ✅                        ║
║           §5 REALD-Protokoll:  ✅                        ║
║           → SENTINEL: ✅ SENTINEL-OK                     ║
╠══════════════════════════════════════════════════════════╣
║ STATUS:   ✅ COMMIT FREIGEGEBEN                          ║
╚══════════════════════════════════════════════════════════╝
```

**Commit-Message-Format:**
```
[SLICE-N] Kurzbeschreibung

TAG-GUARD:
  BUILDER:  ✅ I/O-Clean, Zero-Mock
  CRITIC:   ✅ Mock-Scan CLEAN | Typecheck CLEAN
  SENTINEL: ✅ SENTINEL-OK (5/5 Gesetze)
```

---

## HARD-FAIL ESKALATIONSWEG

```
HARD-FAIL erkannt
      │
      ▼
Fehlerbeschreibung ausgeben (konkret, kein "unbekannter Fehler")
      │
      ▼
STOPP — kein weiterer Code
      │
      ▼
Zurück zu PHASE 3 (PLAN) — Slice neu definieren
      │
      ▼
SPEC neu validieren mit User (§4 Menschliche Hoheit)
      │
      ▼
Erst dann: neuer Builder-Versuch
```

---

## SCRIPT-INTEGRATION

```powershell
# Alles in einem Befehl:
python .agent/skills/rb_police/scripts/rb_tag_check.py --all

# Ausgabe:
# [TAG] BUILDER:  ✅
# [TAG] CRITIC:   ✅ (Mock-Scan: 0 Findings, Hard-Fail: OK)
# [TAG] SENTINEL: ✅ (manuell zu bestätigen)
# [TAG] STATUS:   COMMIT FREIGEGEBEN / HARD-FAIL
```

---

## CONSTRAINTS

- **NIEMALS** den TAG-Dialog überspringen — auch bei "kleinen Fixes"
- **NIEMALS** einen HARD-FAIL mit Workaround beheben — zurück zu PLAN
- **NIEMALS** als Builder committen — nur der Sentinel darf commiten
- **IMMER** das Protokoll-Format ausgeben — nachvollziehbar, nicht zusammengefasst
