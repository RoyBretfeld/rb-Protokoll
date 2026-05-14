---
description: Cloud-Synchronisation (Google Drive) via Robocopy.
---

# Sync: Cloud-Synchronisation

Dieser Workflow synchronisiert das Stammverzeichnis (`E:\_____1111____Projekte-Programmierung\Antigravity`) mit dem Google-Drive-Ziel (`G:\Meine Ablage\_Projekte-Programmierung\Antigravity\`).

## 📍 PRÜFUNG

Vor der Synchronisation wird das Ziel (G:-Laufwerk) auf Verfügbarkeit geprüft. Virtuelle Umgebungen und Meta-Daten (`.git`, `node_modules`, `venv`, etc.) werden **ausgeschlossen**.

## 📍 SCHRITTE

1. **Ziel-Bestätigung:** Prüfe ob das Cloud-Laufwerk G: eingebunden ist.
2. **Synchronisation (Mirror):**
// turbo
```powershell
powershell -ExecutionPolicy Bypass -File .agent/skills/rb_sync/scripts/sync.ps1
```
3. **Validierung:** Prüfe den Robocopy-Exit-Code (0-7 ist Erfolg).
4. **Log-Pfad:** Der Pfad zum Log-File wird im Terminal ausgegeben.

## 📍 VARIANTEN

- **Dry-Run (Vorschau):**
```powershell
powershell -ExecutionPolicy Bypass -File .agent/skills/rb_sync/scripts/sync.ps1 -DryRun
```
- **Kopieren (Kein Löschen am Ziel):**
```powershell
powershell -ExecutionPolicy Bypass -File .agent/skills/rb_sync/scripts/sync.ps1 -NoMirror
```
