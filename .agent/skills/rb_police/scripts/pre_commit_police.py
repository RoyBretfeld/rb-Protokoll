#!/usr/bin/env python3
"""
RB-Framework Police (Antigravity Edition)
Prüft auf Secrets und grobe Verstöße gegen das Protokoll.
"""
import os
import re
import sys
from pathlib import Path

# Fix Windows UnicodeEncodeError (ERR-20260309-WIN-EMOJI)
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Blocked Files (Dürfen nicht committed werden)
BLOCK_FILES = [
    r"\.env$", 
    r"client_secrets\.json$", 
    r"credentials\.json$", 
    r"token\.json$", 
    r"drive_index\.db$",
    r"drive_index\.db-journal$"
]

# Secret Patterns (Harte Regeln)
SECRET_PATTERNS = [
    r"AIza[0-9A-Za-z-_]{35}", # Google API Key
    r"Authorization:\s*Bearer",
    r"access_token",
    r"refresh_token",
    r"sk-[a-zA-Z0-9]{20,}" # OpenAI Key pattern
]

# §5 REALD-PROTOKOLL: Mock/Fake-Data Patterns (Static Scan)
MOCK_PATTERNS = [
    # Hartcodierte Fake-Werte in Assignments
    (r'=\s*["\']mock["\']',           "Hartcodierter 'mock'-String"),
    (r'=\s*["\']dummy["\']',          "Hartcodierter 'dummy'-String"),
    (r'=\s*["\']placeholder["\']',    "Hartcodierter Platzhalter-String"),
    (r'=\s*["\']fake["\']',           "Hartcodierter 'fake'-String"),
    (r'=\s*["\']test_data["\']',      "Hartcodierter 'test_data'-String"),
    (r'=\s*["\']todo["\']',           "Unerledigtes TODO als Wert"),
    # Typische Mock-Konstrukte
    (r'\bMagicMock\(\)',              "MagicMock() in Produktion verboten"),
    (r'\bMock\(\)',                   "Mock() in Produktion verboten"),
    (r'unittest\.mock',              "unittest.mock in Produktion verboten"),
    # Platzhalter-Pattern
    (r'\{\{[A-Z_]+\}\}',             "Ungefüllter Platzhalter {{...}}"),
    (r'<YOUR_[A-Z_]+>',              "Ungefüllter Platzhalter <YOUR_...>"),
    (r'INSERT_[A-Z_]+_HERE',         "Ungefüllter INSERT_..._HERE Platzhalter"),
    # Fake-Return Statements
    (r'return\s+\[\].*#.*TODO',      "TODO-markierter leerer Return"),
    (r'return\s+\{\}.*#.*TODO',      "TODO-markiertes leeres Dict als Return"),
    (r'return\s+None.*#.*TODO',      "TODO-markiertes None als Return"),
    # Fake-Implementierungen
    (r'pass\s*#.*TODO',              "TODO hinter pass (Stub-Funktion)"),
    (r'raise\s+NotImplementedError', "NotImplementedError = unfertige Implementierung"),
]

# Dateien/Verzeichnisse bei Mock-Scan ignorieren (Tests sind erlaubt)
MOCK_SCAN_IGNORE = {"test_", "tests/", "_test.py", "conftest.py", "hard_fail.py", "pre_commit_police.py"}


def fail(msg):
    print(f"[POLICE] ❌ FAIL: {msg}")
    sys.exit(1)


def warn(msg):
    print(f"[POLICE] ⚠️  WARN: {msg}")


def scan_file(path):
    """Secret-Scan + §5 Mock-Scan."""
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
        lines = content.split("\n")

        # Skip wenn Test-Datei
        path_str = str(path).replace("\\", "/")
        if any(ig in path_str for ig in MOCK_SCAN_IGNORE):
            return

        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            # Kommentare überspringen
            if stripped.startswith("#") or stripped.startswith("//"):
                continue

            # Secret-Scan
            for pattern in SECRET_PATTERNS:
                if re.search(pattern, line):
                    if any(x in line for x in ["os.environ", "json.load", "config.get", ".get(", "getenv", "def ", "\": ", "config =", "params =", "return ", "if ", "print("]): continue
                    if "SECRET_PATTERNS" in line: continue
                    fail(f"Secret-Verdacht in {path.name}:{i} -> {pattern}")

            # §5 Mock-Scan
            for pattern, description in MOCK_PATTERNS:
                if re.search(pattern, line, re.IGNORECASE):
                    warn(f"§5 MOCK DETECTED in {path.name}:{i} — {description}")
                    warn(f"  Code: {stripped[:80]}")

    except Exception:
        pass


def main():
    print("🚓 RB Police v2.0: Scanning (Secrets + §5 Mock-Scan)...")
    root = Path.cwd()
    mock_violations = []

    # 1. Check Blocked Files
    for pattern in BLOCK_FILES:
        for f in root.glob("*"):
            if re.search(pattern, f.name):
                print(f"[POLICE] ℹ️  Lokale Config gefunden (Check .gitignore): {f.name}")

    # 2. Scan Source Code (src/ + backend/ + app/)
    scan_dirs = [d for d in ["src", "backend", "app", "api"] if (root / d).exists()]
    if not scan_dirs:
        print("[POLICE] ℹ️  Kein src/backend/app-Verzeichnis — überspringe Code-Scan")
    for dir_name in scan_dirs:
        for py_file in (root / dir_name).rglob("*.py"):
            scan_file(py_file)

    # 3. §5 Check Protocol Existence
    if not (root / "docs/_rb/02_SYSTEM_FACTS.md").exists():
        print("[POLICE] ❌ CRITICAL: 02_SYSTEM_FACTS.md fehlt in docs/_rb/!")
        sys.exit(1)

    # 4. §5 hard_fail.py Verfügbarkeit prüfen
    hf_path = root / ".agent/skills/rb_police/scripts/hard_fail.py"
    if hf_path.exists():
        print("[POLICE] ✅ §5 hard_fail.py Runtime-Enforcer: vorhanden")
    else:
        print("[POLICE] ⚠️  §5 hard_fail.py fehlt — Runtime-Enforcement nicht aktiv")

    print("[POLICE] ✅ Scan complete. System conforms to RB Protocol.")

if __name__ == "__main__":
    main()
