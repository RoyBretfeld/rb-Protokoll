# 🔄 RB-Protokoll v3.0 – Migrations-Plan

> **Codename:** "Metamorphose"
> **Erstellt:** 2026-02-19
> **Status:** ✅ ABGESCHLOSSEN (2026-02-19)
> **Risikostufe:** MITTEL (reversibel via Git)

---

## 0. Zusammenfassung

Das RB-Protokoll wird von einem **dokumenten-zentrierten System** (lose MD-Dateien + Python-Skripte)
in ein **skills-natives System** migriert, das der Agent nativ erkennt und ausführen kann.

**Kernprinzip:** Jede Fähigkeit des Protokolls wird ein eigenständiger, portabler Skill.
Jeder Befehl wird ein Workflow (Slash-Command).

---

## 1. IST-Zustand (v2.x)

### 1.1 Dateien und ihre Rollen

| Datei | Typ | Rolle | Status |
|---|---|---|---|
| `docs/_rb/00_BOOT_PROTOCOL.md` | Passiv-Doc | Startup-Regeln | ✅ Aktiv, aber nur Text |
| `docs/_rb/01_AGENT_LOOP.md` | Passiv-Doc | Arbeitsschleife | ✅ Aktiv, 12 Zeilen |
| `docs/_rb/02_SYSTEM_FACTS.md` | Konfig-Doc | Projektkontext | ⚠️ Template-Platzhalter |
| `docs/_rb/03_ERROR_DB.md` | Datenbank | Fehlerwissen | ✅ Aktiv |
| `docs/_rb/03_ERROR_DB_POINTER.md` | Verweis | Zeigt auf zentrale DB | ✅ Aktiv |
| `docs/_rb/04_STANDARDS.md` | Passiv-Doc | Code-Regeln + 4 Gesetze | ⚠️ Duplikat von 04_UX_LAWS |
| `docs/_rb/04_UX_LAWS.md` | Passiv-Doc | Identisch mit 04_STANDARDS | ⚠️ Duplikat |
| `docs/_rb/05_SECURITY.md` | Template | Sicherheitsregeln | ⚠️ Viele Platzhalter |
| `docs/_rb/06_TEST_MATRIX.md` | Template | Test-Zuordnungen | ⚠️ Viele Platzhalter |
| `docs/_rb/BOOTSTRAP_PROMPT.md` | Prompt | Bootstrap-Anweisung | ✅ Aktiv |
| `scripts/rb.py` | Python CLI | Zentrales Werkzeug | ✅ Funktional |
| `scripts/pre_commit_police.py` | Python Tool | Security-Scanner | ✅ Funktional |
| `scripts/packer.py` | Python Tool | Context-Dump-Generator | ✅ Funktional |
| `scripts/setup_hooks.py` | Python Tool | Git-Hook Installer | ✅ Funktional |
| `scripts/compare_projects.py` | Python Tool | Projektvergleich | ✅ Funktional |
| `rb_bootstrap/installer.py` | Python Tool | Projekt-Bootstrapper | ✅ Funktional |
| `rb_bootstrap/template_rules.yaml` | YAML Konfig | Template für neue Projekte | ✅ Aktiv |

### 1.2 Identifizierte Probleme

1. **Fragmentierung** – 5 Python-Skripte, 10 MD-Dateien, 1 YAML – kein einheitliches System
2. **Passive Docs** – Agent liest `04_UX_LAWS.md`, kann aber nicht dagegen prüfen
3. **Tote Platzhalter** – `05_SECURITY.md` und `06_TEST_MATRIX.md` sind zu ~70% Platzhalter
4. **Duplikate** – `04_STANDARDS.md` = `04_UX_LAWS.md` (identischer Inhalt)
5. **Monolithischer MEMORY-Block** – ~2.000 Zeichen bei JEDER Nachricht
6. **Keine native Integration** – `.agent/skills/` und `.agent/workflows/` existieren nicht

---

## 2. SOLL-Zustand (v3.0)

### 2.1 Neue Verzeichnisstruktur

```
_rb-Protokoll/
│
├── .agent/                              🧠 NATIVE AGENT-INTEGRATION
│   │
│   ├── skills/
│   │   ├── rb_bootstrap/
│   │   │   ├── SKILL.md                 # Boot + Init + Reparatur
│   │   │   ├── scripts/
│   │   │   │   └── installer.py         # ← von rb_bootstrap/
│   │   │   └── templates/
│   │   │       ├── system_facts.template.md
│   │   │       └── template_rules.yaml  # ← von rb_bootstrap/
│   │   │
│   │   ├── rb_police/
│   │   │   ├── SKILL.md                 # Security Audit Skill
│   │   │   └── scripts/
│   │   │       └── pre_commit_police.py # ← von scripts/
│   │   │
│   │   ├── rb_packer/
│   │   │   ├── SKILL.md                 # Context-Dump Generator
│   │   │   └── scripts/
│   │   │       └── packer.py            # ← von scripts/
│   │   │
│   │   ├── ux_guardian/
│   │   │   ├── SKILL.md                 # Die 4 UX-Gesetze als AKTIVER Prüfer
│   │   │   └── resources/
│   │   │       └── checklist.md         # Kompakte Prüfliste
│   │   │
│   │   └── error_learner/
│   │       ├── SKILL.md                 # Error-DB Management
│   │       └── templates/
│   │           └── error_entry.template.md
│   │
│   └── workflows/
│       ├── check.md                     # /check → Police + Baseline
│       ├── bootstrap.md                 # /bootstrap → Umgebung prüfen
│       ├── pack.md                      # /pack → Context Dump
│       ├── flow-close.md                # /flow-close → Nav-Check + UX-Audit
│       ├── learn.md                     # /learn → Error-DB Eintrag
│       └── sentinelcheck.md             # /sentinelcheck → Bestehend
│
├── docs/
│   └── _rb/
│       ├── 02_SYSTEM_FACTS.md           # Bleibt (projektspezifisch, kein Skill)
│       └── 03_ERROR_DB.md               # Bleibt (wachsendes Wissen)
│
├── _archive/                            # Alte Dateien (nicht gelöscht!)
│   ├── docs_rb_v2/                      # Backup der alten docs/_rb/
│   └── scripts_v2/                      # Backup der alten scripts/
│
├── CHANGELOG.md                         # Aktualisiert
├── README.md                            # Aktualisiert mit neuem Quick-Start
└── MIGRATION_PLAN_v3.md                 # Dieses Dokument
```

### 2.2 Skill-Definitionen (Vorschau)

#### Skill 1: `rb_bootstrap`
```yaml
---
name: RB Bootstrap
description: >
  Prüft und repariert die RB-Protokoll-Umgebung. Verifiziert
  Verzeichnisstruktur, Pflichtdateien und Konfiguration.
  Ersetzt 00_BOOT_PROTOCOL + 01_AGENT_LOOP + installer.py.
version: 3.0.0
triggers: ["Bootstrap jetzt", "/bootstrap"]
---
```
**Vereint:** `00_BOOT_PROTOCOL.md` + `01_AGENT_LOOP.md` + `BOOTSTRAP_PROMPT.md` + `rb_bootstrap/installer.py`

#### Skill 2: `rb_police`
```yaml
---
name: RB Police
description: >
  Security-Scanner. Prüft auf Secrets, verbotene Dateien
  und Protokoll-Verstöße. Integriert 05_SECURITY Regeln.
version: 3.0.0
triggers: ["Police", "/check"]
---
```
**Vereint:** `pre_commit_police.py` + `05_SECURITY.md`

#### Skill 3: `rb_packer`
```yaml
---
name: RB Packer
description: >
  Erzeugt strukturierte Context-Dumps für Agent-Kontext
  oder Debugging. Auto-Detection von Projektverzeichnissen.
version: 3.0.0
triggers: ["Pack", "/pack"]
---
```
**Vereint:** `packer.py` + `compare_projects.py`

#### Skill 4: `ux_guardian`
```yaml
---
name: UX Guardian
description: >
  Aktiver Hüter der 4 UX-Gesetze (Transparenz, Revidierbarkeit,
  Progressive Offenlegung, Menschliche Hoheit). Prüft UI-Änderungen
  gegen die Checkliste.
version: 3.0.0
triggers: ["Flow schließen", "UX prüfen"]
---
```
**Vereint:** `04_UX_LAWS.md` + `04_STANDARDS.md` (Duplikat aufgelöst)

#### Skill 5: `error_learner`
```yaml
---
name: Error Learner
description: >
  Strukturiertes Erfassen neuer Fehler in der Error-DB.
  Bietet Templates und Validierung für konsistente Einträge.
version: 3.0.0
triggers: ["Learn", "/learn"]
---
```
**Vereint:** `rb.py learn`-Command + Error-DB-Logik

### 2.3 Workflow-Definitionen (Vorschau)

#### `/check` Workflow
```markdown
---
description: Pre-Commit Gate – Police + Baseline Tests
---
// turbo-all
1. Lies `.agent/skills/rb_police/SKILL.md` für Kontext
2. Führe aus: `python .agent/skills/rb_police/scripts/pre_commit_police.py`
3. Prüfe ob `docs/_rb/03_ERROR_DB.md` existiert
4. Wenn Baseline-Tests konfiguriert: Ausführen
5. Ergebnis: ✅ Grün oder ❌ mit Details
```

#### `/bootstrap` Workflow
```markdown
---
description: RB-Umgebung prüfen und reparieren
---
1. Lies `.agent/skills/rb_bootstrap/SKILL.md`
2. Prüfe Verzeichnisstruktur gegen Soll
3. Prüfe Pflichtdateien (SYSTEM_FACTS, ERROR_DB)
4. Identifiziere unfilled Placeholders
5. Bei Fehlern: Reparaturvorschlag
```

#### `/flow-close` Workflow
```markdown
---
description: Flow-Integrität prüfen – Navigation + UX-Audit
---
1. Navigations-Check (Rückweg zum Root sicherstellen)
2. Lies `.agent/skills/ux_guardian/SKILL.md`
3. Prüfe letzte Änderungen gegen die 4 Gesetze
4. Nur beenden wenn alles "Grün"
```

---

## 3. Migrations-Phasen

### Phase 1: Skills erstellen ✅ ERLEDIGT
- [x] `.agent/skills/rb_bootstrap/SKILL.md` schreiben
- [x] `.agent/skills/rb_police/SKILL.md` schreiben
- [x] `.agent/skills/rb_packer/SKILL.md` schreiben
- [x] `.agent/skills/ux_guardian/SKILL.md` schreiben
- [x] `.agent/skills/error_learner/SKILL.md` schreiben
- [x] Python-Skripte in Skill-Ordner **kopiert**

**Validierung:** ✅ 5/5 Skills mit Skripten vorhanden

### Phase 2: Workflows erstellen ✅ ERLEDIGT
- [x] `.agent/workflows/check.md` schreiben
- [x] `.agent/workflows/bootstrap.md` schreiben
- [x] `.agent/workflows/pack.md` schreiben
- [x] `.agent/workflows/flow-close.md` schreiben
- [x] `.agent/workflows/learn.md` schreiben
- [x] `.agent/workflows/sentinelcheck.md` schreiben

**Validierung:** ✅ 6/6 Workflows vorhanden

### Phase 3: Aufräumen ✅ ERLEDIGT
- [x] `_archive/docs_rb_v2/` erstellt → 8 alte Docs verschoben
- [x] `_archive/scripts_v2/` erstellt → 5 alte Skripte verschoben
- [x] `_archive/rb_bootstrap_v2/` erstellt → Installer + Payload verschoben
- [x] Duplikat `04_STANDARDS.md` archiviert (= `04_UX_LAWS.md`)
- [x] Platzhalter-Dateien archiviert
- [x] `README.md` aktualisiert
- [x] `CHANGELOG.md` aktualisiert (v3.0.0 Entry)
- [x] Leere Ordner `scripts/` und `rb_bootstrap/` entfernt
- [x] **Globaler LLM-Packer Skill** in `GLOBALE_SKILLS/llm_packer/` erstellt

**Validierung:** ✅ `docs/_rb/` enthält nur 02_SYSTEM_FACTS + 03_ERROR_DB

### Phase 4: MEMORY-Optimierung ✅ VORSCHLAG ERSTELLT
- [x] Neuer schlanker MEMORY-Block vorgeschlagen (siehe `docs/MEMORY_OPTIMIZATION_v3.md`)
- [ ] User bestätigt und aktualisiert Settings → **OFFEN**

---

## 4. Was wird NICHT migriert

| Datei | Grund | Verbleib |
|---|---|---|
| `02_SYSTEM_FACTS.md` | Projektspezifisch, kein Skill | Bleibt in `docs/_rb/` |
| `03_ERROR_DB.md` | Wachsende Datenbank | Bleibt in `docs/_rb/` |
| `03_ERROR_DB_POINTER.md` | Verweis auf zentrale DB | Wird in Bootstrap-Skill integriert |
| `CHANGELOG.md` | Projekt-Meta | Bleibt, wird aktualisiert |
| `README.md` | Projekt-Meta | Bleibt, wird aktualisiert |

---

## 5. Risiken und Mitigationen

| Risiko | Schwere | Mitigation |
|---|---|---|
| Agent findet Skills nicht | HOCH | `.agent/` muss im Workspace-Root liegen → Struktur verifizieren |
| Alte Pfade in MEMORY brechen | MITTEL | Phase 3 erst nach Phase 1+2 Validierung |
| Python-Skripte haben relative Pfade | NIEDRIG | Skripte werden kopiert, nicht verschoben; alte bleiben als Backup |
| User verliert gewohnte Befehle | NIEDRIG | Workflows bilden exakt die gleichen Commands ab |

---

## 6. Rollback-Strategie

**Alles ist reversibel:**
1. Git-Status prüfen: `git status` → alle Änderungen sichtbar
2. `_archive/` enthält 1:1 Kopien des alten Zustands
3. Im Extremfall: `git checkout .` → Komplett-Reset

---

## 7. Erwarteter Gewinn

| Metrik | Vorher (v2.x) | Nachher (v3.0) |
|---|---|---|
| MEMORY-Verbrauch pro Nachricht | ~2.000 Zeichen | ~300 Zeichen |
| Aktive Dateien im System | 16+ lose Dateien | 5 Skills + 5 Workflows |
| Duplikate | 3 (Standards, UX Laws, Error DB) | 0 |
| Tote Platzhalter-Dateien | 3 | 0 |
| Agent kann Skill ausführen | ❌ Nur lesen | ✅ Nativ |
| Portabilität (neues Projekt) | Manuell kopieren | `.agent/` Ordner kopieren |
| Slash-Command Support | 1 (`/sentinelcheck`) | 6 |

---

## 8. Freigabe

> ✅ **Alle Phasen abgeschlossen am 2026-02-19.**

- [x] **DONE** Phase 1 – Skills erstellt (5/5)
- [x] **DONE** Phase 2 – Workflows erstellt (6/6)
- [x] **DONE** Phase 3 – Aufgeräumt + Globaler Packer-Skill
- [x] **DONE** Phase 4 – MEMORY-Vorschlag erstellt
- [ ] **OFFEN** – User aktualisiert MEMORY[user_global] in Settings
