#!/usr/bin/env python3
"""
hard_fail.py — §5 REALD-PROTOKOLL Enforcement
RB-Framework (Antigravity Edition) | v1.0

ZWECK:
    Wenn echte Daten erwartet werden, aber nur Mocks/Platzhalter vorhanden sind,
    MUSS das System sofort mit einem klaren Fehler abstürzen.
    Kein stilles Weiterarbeiten. Kein freundlicher Fallback.

VERWENDUNG in Projekten:
    from hard_fail import real_or_die, no_mock, assert_real_io

REGEL §5 REALD-PROTOKOLL:
    "Mockdaten sind riesengroßer Mist und verstecken Fehler."
    Wenn kein echter I/O da ist -> knallt es. Sofort.
"""

import os
import sys
import inspect
from typing import Any


# ──────────────────────────────────────────────
# SENTINEL VALUES (bekannte Fake-Werte)
# ──────────────────────────────────────────────

_MOCK_STRINGS = {
    # Platzhalter-Strings
    "todo", "fixme", "placeholder", "mock", "fake", "dummy",
    "test_data", "sample", "example_data", "lorem ipsum",
    "your_api_key", "insert_key_here", "xxx", "changeme",
    "your-token-here", "replace_me", "abc123", "password123",
    # Typische KI-Generated Fake-IDs
    "user_123", "user_456", "item_1", "item_2", "id_001",
    "test@example.com", "foo@bar.com", "admin@test.com",
}

_MOCK_DICT_KEYS_PATTERN = {
    # Dicts, die wie Mock-Responses aussehen
    "mock_response", "fake_data", "dummy_result", "static_data",
    "hardcoded", "placeholder_data",
}


class MockDataError(RuntimeError):
    """
    Wird geworfen, wenn Mock-/Fake-Daten im System erkannt werden.
    §5 REALD-PROTOKOLL Verletzung.
    """
    def __init__(self, msg: str, caller: str = ""):
        prefix = f"[§5 HARD-FAIL] {caller}: " if caller else "[§5 HARD-FAIL] "
        super().__init__(
            f"\n{'='*60}\n"
            f"{prefix}MOCK DATA DETECTED!\n"
            f"  {msg}\n"
            f"  -> Kein Fake-Fallback erlaubt (§5 REALD-PROTOKOLL)\n"
            f"  -> Echter I/O erforderlich. System gestoppt.\n"
            f"{'='*60}"
        )


def _caller_info() -> str:
    """Gibt Datei + Zeilennummer des Aufrufers zurück."""
    frame = inspect.stack()[2]
    return f"{os.path.basename(frame.filename)}:{frame.lineno}"


# ──────────────────────────────────────────────
# KERN-FUNKTIONEN
# ──────────────────────────────────────────────

def real_or_die(value: Any, name: str = "value") -> Any:
    """
    Prüft ob ein Wert ein bekannter Mock/Platzhalter ist.
    Wenn ja: sofortiger Hard-Fail.

    Verwendung:
        api_key = real_or_die(os.getenv("API_KEY"), "API_KEY")
        data    = real_or_die(fetch_from_db(), "db_result")
    """
    caller = _caller_info()

    # None / leere Werte
    if value is None:
        raise MockDataError(f"'{name}' ist None — echter Wert erwartet.", caller)

    if isinstance(value, str):
        if not value.strip():
            raise MockDataError(f"'{name}' ist ein leerer String.", caller)
        if value.strip().lower() in _MOCK_STRINGS:
            raise MockDataError(f"'{name}' = '{value}' ist ein bekannter Mock-String.", caller)
        # Platzhalter-Pattern {{ }} und < >
        if value.startswith("{{") or value.startswith("<") and value.endswith(">"):
            raise MockDataError(f"'{name}' = '{value}' ist ein ungefüllter Platzhalter.", caller)

    if isinstance(value, list) and len(value) == 0:
        raise MockDataError(f"'{name}' ist eine leere Liste — echter Datensatz erwartet.", caller)

    if isinstance(value, dict):
        if len(value) == 0:
            raise MockDataError(f"'{name}' ist ein leeres Dict.", caller)
        # Prüfe ob Keys nach Mock-Pattern aussehen
        for key in value.keys():
            if str(key).lower() in _MOCK_DICT_KEYS_PATTERN:
                raise MockDataError(
                    f"'{name}' hat einen verdächtigen Mock-Key: '{key}'.", caller
                )

    return value  # Alles OK — echter Wert durchgelassen


def no_mock(func):
    """
    Decorator: Markiert eine Funktion als Mock-frei.
    Wirft sofort MockDataError wenn die Funktion None oder
    einen bekannten Fake-Wert zurückgibt.

    Verwendung:
        @no_mock
        def fetch_user(user_id: str) -> dict:
            return db.query(user_id)
    """
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return real_or_die(result, name=func.__name__ + "()")
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


def assert_real_io(condition: bool, context: str = ""):
    """
    Explizite I/O-Assertion. Für Stellen, wo du sicher sein musst,
    dass echter I/O stattgefunden hat.

    Verwendung:
        rows = db.fetchall()
        assert_real_io(len(rows) > 0, "DB-Abfrage muss Ergebnisse liefern")

        response = requests.get(url)
        assert_real_io(response.status_code == 200, f"API {url}")
    """
    if not condition:
        caller = _caller_info()
        msg = context if context else "I/O-Assertion fehlgeschlagen"
        raise MockDataError(msg, caller)


def env_or_die(key: str) -> str:
    """
    Liest eine Umgebungsvariable. Wenn sie fehlt oder leer/fake ist:
    sofortiger Hard-Fail.

    Verwendung:
        api_key = env_or_die("GROQ_API_KEY")
        db_url  = env_or_die("DATABASE_URL")
    """
    val = os.environ.get(key)
    if not val:
        raise MockDataError(
            f"Umgebungsvariable '{key}' ist nicht gesetzt.",
            _caller_info()
        )
    return real_or_die(val, name=key)


# ──────────────────────────────────────────────
# SELF-TEST (python hard_fail.py)
# ──────────────────────────────────────────────

if __name__ == "__main__":
    print("=== hard_fail.py Self-Test ===\n")
    passed = 0
    failed = 0

    tests = [
        ("None erkennen",          lambda: real_or_die(None, "x")),
        ("Leerer String",          lambda: real_or_die("", "x")),
        ("'mock' String",          lambda: real_or_die("mock", "x")),
        ("Platzhalter {{KEY}}",    lambda: real_or_die("{{MY_KEY}}", "x")),
        ("Leere Liste",            lambda: real_or_die([], "x")),
        ("Leeres Dict",            lambda: real_or_die({}, "x")),
        ("assert_real_io False",   lambda: assert_real_io(False, "Test IO")),
        ("env_or_die fehlend",     lambda: env_or_die("__RB_NON_EXISTENT_VAR__")),
    ]

    for name, fn in tests:
        try:
            fn()
            print(f"  [FAIL] {name} — KEIN Error geworfen! (Bug in hard_fail)")
            failed += 1
        except MockDataError as e:
            print(f"  [OK]   {name} -> MockDataError korrekt ausgelöst")
            passed += 1

    # Positiv-Test: echter Wert darf nicht crashen
    try:
        real_or_die("echter_wert", "x")
        real_or_die({"key": "val"}, "x")
        real_or_die([1, 2, 3], "x")
        print(f"  [OK]   Echte Werte werden durchgelassen")
        passed += 1
    except MockDataError as e:
        print(f"  [FAIL] Echter Wert fälschlicherweise blockiert: {e}")
        failed += 1

    print(f"\nErgebnis: {passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)
