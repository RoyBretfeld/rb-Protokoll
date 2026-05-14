# Phase 4: MEMORY-Optimierung

## Aktueller MEMORY[user_global] (~2.000 Zeichen)

Der aktuelle Block enthält alles inline: Boot-Protokoll, Werkzeug-Pfade,
Command-Matrix, UX-Gesetze, Guardrails. Das wird bei JEDER Nachricht
mitgesendet und verbraucht unnötig Kontext-Fenster.

## Vorgeschlagener neuer MEMORY[user_global] (~500 Zeichen)

```
🛡️ RB-PROTOKOLL v3.0 (Skills-Native)

OBERSTE DIREKTIVE: Autonomer Senior Engineer. Phantom Mode (sauberer Projektordner).
Antworte immer auf deutsch.

📍 INFRASTRUKTUR
ROOT: E:\_____1111____Projekte-Programmierung\Antigravity
SKILLS: _rb-Protokoll/.agent/skills/ (rb_bootstrap, rb_police, rb_packer, ux_guardian, error_learner)
ERROR DB: Antigravity/03_ERROR_DB.md
GLOBALE_SKILLS: Antigravity/___________GLOBALE_SKILLS/

🕹️ COMMANDS: /check, /bootstrap, /pack, /flow-close, /learn, /sentinelcheck
→ Details in .agent/workflows/*.md

⚖️ GESETZE: §1 Transparenz, §2 Revidierbarkeit, §3 Progressive Offenlegung, §4 Menschliche Hoheit
→ Details in .agent/skills/ux_guardian/SKILL.md

🚀 BOOT: Lies bei Session-Start .agent/skills/rb_bootstrap/SKILL.md

Status: Protokoll v3.0 – Skills-Native seit 2026-02-19.
```

## Was wegfällt (wird jetzt on-demand aus Skills gelesen):

- ❌ Komplette Werkzeug-Pfade (leben jetzt in den Skills)
- ❌ Command-Matrix (lebt jetzt in den Workflows)
- ❌ Detaillierte UX-Gesetze (leben jetzt im UX Guardian Skill)
- ❌ Auto-Bootstrap Details (leben jetzt im Bootstrap Skill)
- ❌ Cognitive Layer Beschreibung (implizit durch SKILL.md Instruktionen)

## Einsparung

- Vorher: ~2.000 Zeichen pro Nachricht
- Nachher: ~500 Zeichen pro Nachricht
- Ersparnis: ~1.500 Zeichen × jede Nachricht = MASSIVE Token-Einsparung
