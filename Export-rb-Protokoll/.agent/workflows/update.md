---
description: Aktualisiert das RB-Protokoll in einem bestehenden Projekt auf den neusten Stand
---

# /update — RB-Protokoll Updater

Dieser Workflow aktualisiert alle Protokoll-Core-Dateien in einem bestehenden Projekt.
Er schützt dabei **alle projekt-spezifischen Dateien** (SYSTEM_FACTS, ERROR_DB, .env, etc.)

## Wann nutzen?

- Ein Projekt läuft noch auf einer älteren Protokoll-Version
- Neue Skills/Workflows wurden im Export-Paket hinzugefügt
- Nach einem Protokoll-Release (z.B. neuer MAR-Workflow, neuer §...)
- Regelmäßig als Wartungsaufgabe (empfohlen: monatlich)

## Schritte

// turbo-all

1. **Dry-Run ausführen (immer zuerst!):**
   ```powershell
   python "E:\_____1111____Projekte-Programmierung\Antigravity\_rb-Protokoll\Export-rb-Protokoll\.agent\skills\rb_police\scripts\rb_updater.py" --target "."
   ```
   Liest: Was würde sich ändern? Schreibt nichts.

2. **Update ausführen (nach Prüfung):**
   ```powershell
   python "E:\_____1111____Projekte-Programmierung\Antigravity\_rb-Protokoll\Export-rb-Protokoll\.agent\skills\rb_police\scripts\rb_updater.py" --target "." --apply
   ```
   Erstellt Backup in `_archive/rb_update_DATUM/` bevor es ändert.

3. **Für Automation / CI (keine Rückfrage):**
   ```powershell
   python "...rb_updater.py" --target "." --apply --force
   ```

## Was wird geupdated?

| Kategorie | Dateien | Update? |
|---|---|---|
| Protokoll-Core | `01_MISSION_PROMPT.md`, `01_PLAN_EXECUTION.md`, etc. | ✅ Ja |
| Skills | `.agent/skills/*/SKILL.md` | ✅ Ja |
| Scripts | `pre_commit_police.py`, `hard_fail.py`, `packer.py` | ✅ Ja |
| Workflows | `.agent/workflows/*.md` | ✅ Ja |
| **NIEMALS** | `02_SYSTEM_FACTS.md`, `03_ERROR_DB.md`, `.env` | ❌ Protected |

## Garantien (§2 Revidierbarkeit)

- Vor jedem Schreiben: Backup in `_archive/rb_update_DATUM/`
- Dry-Run ist Default: ohne `--apply` passiert nichts
- Nur Whitelist-Dateien werden angefasst — niemals freier Zugriff

## Ergebnis prüfen

Nach dem Update:
```powershell
cat PROTOCOL_VERSION   # Sollte neue Version zeigen
/bootstrap             # Alle Skills + Workflows valide?
```
