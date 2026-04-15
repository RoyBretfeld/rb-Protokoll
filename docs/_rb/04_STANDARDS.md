# 04_STANDARDS

## Code‑Regeln

- Kleine PRs, kleine Diffs.
- Keine "nur mal schnell alles formatieren" Aktionen.
- Naming:
     - Variablen & Funktionen: snake_case (Python-Standard)
     - Klassen: PascalCase
     - Konstanten: UPPER_SNAKE_CASE
     - Dateien/Module: snake_case
     - Private Funktionen: _leading_underscore
     - Code: Englisch
     - UI-Texte & Kommentare: Deutsch

## Architektur‑Regeln

- Trenne: domain / service / persistence / transport (wo sinnvoll)
- Keine Business‑Logik in Templates/UI‑Views.

## Logging

- Keine Secrets.
- Logs müssen debug‑fähig sein: request_id, user_id (wenn erlaubt), timings.
