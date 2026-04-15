# 05_SECURITY

## Secrets

- Verboten im Repo: API‑Keys, Tokens, Passwörter, private keys.
- Verboten in Logs: Authorization Header, DB URLs, SMTP Passwörter.

## Auth/RBAC

- Rollen: Kein RBAC (lokales Tool / Single-User). Bei Multi-User: admin / user / readonly.
- Jede Datenabfrage ist mandanten‑sicher (scope by owner/tenant).

## Uploads

- Allowed MIME: Kein Upload-Feature aktiv. Bei Bedarf: image/jpeg, image/png, application/pdf — kein text/html, kein application/javascript.
- Max size: Kein Upload-Feature aktiv. Bei Bedarf: 10 MB (10485760 Bytes).
- EXIF strip + Thumbnails (wenn Bilder)

## Injections

- SQL: prepared statements/ORM
- XSS: output escaping
- CSRF: token/cookie policy

## Audit/DSGVO (falls relevant)

- Wer hat was gesehen/gelöscht/geladen?
- Export/Löschung möglich.
