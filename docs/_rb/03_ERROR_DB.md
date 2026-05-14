# 03_ERROR_DB — Fehler-Datenbank

Zweck: Wiederkehrende Fehler **einmal** sauber erklären,
damit Mensch und Agent sie nicht wiederholen.

---

## Schema

```
## ERR-YYYYMMDD-KURZNAME

- **Symptom:** Was war sichtbar falsch?
- **Root Cause:** Warum ist es passiert?
- **Fix:** Wie wurde es behoben?
- **Regression Test:** Wie verhindert man Wiederholung?
- **Neue Regel:** Welcher Guardrail wurde ergänzt?
```

---

## Einträge

<!-- Erste Einträge per `rb learn` oder manuell eintragen -->
