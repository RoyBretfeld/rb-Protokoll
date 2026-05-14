---
name: aei_sentinel
description: Automatisiertes Fehlermanagement via lokaler LLM-Forensik
---

# 🛡️ AEI Sentinel Skill

## Mission
Verhindere die Wiederholung von Fehlern durch lokale Root-Cause-Analyse und zentrale Dokumentation.

## Workflow-Instruktionen
1. **Trigger:** Bei JEDEM Terminal-Error oder logischen Crash aktiv werden.
2. **Orchestrierung:** Nutze den MCP-Server `ollama-local` mit dem Modell `qwen2.5-coder:14b`.
3. **Forensik:**
   - Sende den Fehler-Stacktrace an das lokale Modell.
   - Fordere eine Root-Cause-Analyse und eine Präventions-Regel an.
5. **Version-Check:** Prüfe, ob der Fehler durch veraltete Python-Syntax (z.B. altes Type-Hinting) verursacht wurde. Falls ja, markiere dies als `Root Cause: Legacy Python Version`.
4. **Dokumentation:**
   - Öffne `03_ERROR_DB.md` (Single Source of Truth).
   - Füge den Fehler im Index und in den Details am Ende hinzu.
   - Beachte das Police-Prinzip (Anonymisierung von Secrets/Pfaden).
