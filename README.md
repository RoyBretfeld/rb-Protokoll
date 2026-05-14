# 🛡️ RB-Protokoll v3.3.0

> Das Agent-Betriebssystem für saubere, sichere und nachvollziehbare KI-gesteuerte Entwicklung.
> Optimiert für industrielle Engineering-Workflows in Mensch-KI-Teams.

---

## 🎯 Über das RB-Protokoll

Das RB-Protokoll ist ein von Roy Bretfeld entwickeltes industrielles Engineering-Betriebssystem für die Zusammenarbeit zwischen Menschen und KI-Agenten. Es transformiert KI-Assistenten von reinen Code-Generatoren zu verantwortungsvollen Senior Engineers, die nach standardisierten Regeln, Sicherheitsvorgaben und UX-Prinzipien arbeiten.

### Kern-Features:
- **Skills & Workflows:** Standardisierte Slash-Commands (`/check`, `/bootstrap`, `/pack`) für konsistente Qualität.
- **Security-Gate:** Aktive Überwachung von Secrets und Compliance-Regeln (RB Police).
- **Fehler-Gedächtnis:** Zentrale und lokale Error-DB zur Vermeidung repetitiver Fehler.
- **Die 4+1 Gesetze:** UX-Prinzipien (§1-§4) und ein autonomer Betriebsmodus (§5).

---

## 🚀 Quick-Start

Innerhalb eines mit dem RB-Protokoll initialisierten Projekts stehen folgende Commands zur Verfügung:

| Befehl | Aktion | Anwendung |
|---|---|---|
| `/check` | Security-Scan + Baseline-Tests | Vor jedem Commit (Pflicht) |
| `/bootstrap` | Umgebung prüfen & reparieren | Session-Start oder Setup |
| `/pack` | Context-Dump erzeugen | Übergabe an andere Agenten |
| `/flow-close` | UX-Audit (4 Gesetze) | Vor Release / Feature-Abschluss |
| `/learn` | Fehler dokumentieren | Nach gelösten Bugs |
| `/sentinelcheck` | Komplett-Audit | Tiefenprüfung der Integrität |

---

## ⚖️ Die 5 Gesetze

Das Fundament jedes RB-Projekts sind die 5 Gesetze des Protokolls:

1. **§1 Transparenz** – Keine Hintergrund-Magie ohne Feedback.
2. **§2 Revidierbarkeit** – Jede Aktion muss rückgängig machbar sein (Soft-Delete, Undo).
3. **§3 Progressive Offenlegung** – Clean UI, technische Details erst auf Anfrage.
4. **§4 Menschliche Hoheit** – Die KI schlägt vor, der Mensch entscheidet (Human-in-the-Loop).
5. **§5 Plan Execution Autonomy** – Maximale Autonomie bei der Ausführung genehmigter Pläne.

---

## 🐍 Anforderungen

- **Python 3.12+** (Strikte Anforderung für v3.x)
- **Git**

```bash
# Version prüfen
python --version  # Sollte 3.12.x liefern
```

---

## 📁 Struktur

```
.agent/
├── skills/           # Erweiterte Fähigkeiten des Agenten
└── workflows/        # Prozess-Definitionen (Slash-Commands)

docs/_rb/
├── 01_PLAN_EXECUTION.md  # §5 Regelwerk
├── 02_SYSTEM_FACTS.md    # Projekt-Kontext (SSOT)
└── 03_ERROR_DB.md        # Gelerntes Wissen
```

---

## 📜 Lizenz

Dieses Projekt steht unter der **MIT Lizenz**.
Copyright (c) 2026 Roy Bretfeld.

---

## 👤 Kontakt

**Roy Bretfeld**  
KI-Beratung & Prozessautomatisierung  
Website: [rh-automation-dresden.de](https://rh-automation-dresden.de)
