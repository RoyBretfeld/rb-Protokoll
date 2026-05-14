---
name: Cloud Sync
description: "Automatisiertes Synchronisieren des Antigravity-Stammverzeichnisses in die Cloud (Google Drive) unter Ausschluss von virtuellen Umgebungen."
---

# RB-Sync: Cloud-Synchronisation

Dieses Skill ermöglicht die effiziente und sichere Synchronisation des lokalen Projektverzeichnisses mit der Cloud (G:-Laufwerk).

## 📍 INFRASTRUKTUR

- **SKRIPT:** `_rb-Protokoll/.agent/skills/rb_sync/scripts/sync.ps1`
- **Ziele:** 
  - Source: `E:\_____1111____Projekte-Programmierung\Antigravity`
  - Target: `G:\Meine Ablage\_Projekte-Programmierung\Antigravity\`
- **Ausschlüsse:** `.git`, `node_modules`, `venv`, `.venv`, `env`, `.env`, `virtualenv`, `.virtualenv`, `__pycache__`, `.rb_dumps`, `.idea`, `.vscode`, `_archive`, `_rb_dumps`.

## 📍 BEFEHLE

- **Standard (Mirror):** `powershell -ExecutionPolicy Bypass -File .agent/skills/rb_sync/scripts/sync.ps1`
- **Dry-Run (Vergleich):** `powershell -ExecutionPolicy Bypass -File .agent/skills/rb_sync/scripts/sync.ps1 -DryRun`
- **Ohne Mirror (Kopieren):** `powershell -ExecutionPolicy Bypass -File .agent/skills/rb_sync/scripts/sync.ps1 -NoMirror`
- **Cloud-Reinigung (löschen von venvs):** `powershell -ExecutionPolicy Bypass -File .agent/skills/rb_sync/scripts/cleanup_cloud.ps1`

## ⚖️ REGELN

1. **Virtuelle Umgebungen:** Werden niemals synchronisiert, um Cloud-Speicherplatz und Zeit zu sparen.
2. **Logging:** Jede Synchronisation wird in `_rb-Protokoll/logs/sync_<timestamp>.log` protokolliert.
3. **Sicherheit:** Standardmäßig wird `/MIR` (Mirror) verwendet, was Dateien im Ziel löscht, wenn sie lokal nicht mehr vorhanden sind. Dies hält die Cloud sauber.
4. **Verfügbarkeit:** Laufwerk G: muss eingebunden sein.

## 📝 WORKFLOW

### /sync
Führt den Cloud-Abgleich im Standard-Modus (Mirror) aus.
1. Prüfen der Cloud-Erreichbarkeit.
2. Ausführen von Robocopy mit definierten Ausschlüssen.
3. Log-Eintrag erstellen.

### /sync-clean
Reinigt die Cloud (`G:`) von bereits vorhandenen virtuellen Umgebungen (`venv`, `node_modules`), die lokal ignoriert werden.
