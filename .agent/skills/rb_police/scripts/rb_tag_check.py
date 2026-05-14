#!/usr/bin/env python3
"""
rb_tag_check.py — Triple-Agent-Guard Checker
RB-Framework (Antigravity Edition) | TAG v1.0

Führt alle mechanischen Critic-Checks des TAG-Workflows aus.
Kein Mensch entscheidet ob Checks grün sind — das Skript entscheidet.

VERWENDUNG:
    python rb_tag_check.py --mock-scan          # Nur Mock-Scan
    python rb_tag_check.py --hard-fail          # Nur Hard-Fail Check
    python rb_tag_check.py --typecheck          # Nur Typecheck (konfigurierbar)
    python rb_tag_check.py --all                # Alles (Default)
    python rb_tag_check.py --all --dir backend  # Nur bestimmtes Verzeichnis
"""

import re
import sys
import subprocess
import argparse
from pathlib import Path

# Fix Windows UnicodeEncodeError (ERR-20260309-WIN-EMOJI)
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ──────────────────────────────────────────────
# CRITIC MOCK-PATTERNS (erweiterte Liste)
# ──────────────────────────────────────────────
CRITIC_PATTERNS = [
    # Direkte Mock-Strings als Werte
    (r'=\s*["\']mock["\']',            "Mock-String als Wert"),
    (r'=\s*["\']dummy["\']',           "Dummy-String als Wert"),
    (r'=\s*["\']placeholder["\']',     "Placeholder-String als Wert"),
    (r'=\s*["\']fake["\']',            "Fake-String als Wert"),
    (r'=\s*["\']example["\']',         "Example-String als Wert"),
    (r'=\s*["\']temp["\']',            "Temp-String als Wert"),
    (r'=\s*["\']test_data["\']',       "test_data als Wert"),
    (r'=\s*["\']todo["\']',            "TODO als Wert"),
    # Mock-Frameworks in Produktion
    (r'\bMagicMock\(\)',               "MagicMock() in Produktion"),
    (r'\bMock\(\)',                    "Mock() in Produktion"),
    (r'unittest\.mock',               "unittest.mock in Produktion"),
    (r'from\s+unittest\s+import\s+mock', "unittest mock import"),
    # Platzhalter
    (r'\{\{[A-Z_]{2,}\}\}',           "Ungefuellter Platzhalter {{...}}"),
    (r'<YOUR_[A-Z_]+>',               "Platzhalter <YOUR_...>"),
    (r'INSERT_[A-Z_]+_HERE',          "Platzhalter INSERT_..._HERE"),
    # Stub-Code
    (r'raise\s+NotImplementedError',  "NotImplementedError = Stub"),
    (r'pass\s*#.*[Tt][Oo][Dd][Oo]',  "pass mit TODO = Stub"),
    (r'#\s*TODO:.*implement',         "TODO: implement"),
    (r'#\s*FIXME',                    "FIXME im Produktionscode"),
    # Fake Static Returns
    (r'return\s+\[\]\s*#.*TODO',      "Leerer List-Return mit TODO"),
    (r'return\s+\{\}\s*#.*TODO',      "Leeres Dict-Return mit TODO"),
    (r'return\s+None\s*#.*TODO',      "None-Return mit TODO"),
    # Typische KI-generierte Fake-IDs
    (r'["\']user_?12[34567]["\']',    "Hartcodierte Fake-User-ID"),
    (r'["\']test@example\.com["\']',  "Fake-Email test@example.com"),
    (r'["\']admin@test\.com["\']',    "Fake-Email admin@test.com"),
]

# Dateien/Pfade die beim Critic-Scan ignoriert werden
CRITIC_IGNORE_PATHS = {
    "test_", "_test.py", "tests/", "conftest.py",
    "hard_fail.py", "pre_commit_police.py", "rb_tag_check.py",
    ".venv", "node_modules", "__pycache__", ".git"
}

# Quellcode-Erweiterungen die gescannt werden
SCAN_EXTENSIONS = {".py", ".ts", ".tsx", ".js", ".jsx"}


def is_ignored(path: Path) -> bool:
    path_str = str(path).replace("\\", "/")
    return any(ig in path_str for ig in CRITIC_IGNORE_PATHS)


def mock_scan(scan_dirs: list[Path]) -> tuple[bool, list[str]]:
    """
    Critic Check 1: Sucht nach Mock/Placeholder-Pattern im Quellcode.
    Returns: (passed: bool, findings: list[str])
    """
    findings = []

    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            continue
        for ext in SCAN_EXTENSIONS:
            for f in scan_dir.rglob(f"*{ext}"):
                if is_ignored(f):
                    continue
                try:
                    content = f.read_text(encoding="utf-8", errors="ignore")
                    for i, line in enumerate(content.splitlines(), 1):
                        stripped = line.strip()
                        # Kommentare überspringen (außer TODO/FIXME-Checks)
                        if stripped.startswith(("#", "//", "/*", "*")) and "TODO" not in stripped and "FIXME" not in stripped:
                            continue
                        for pattern, description in CRITIC_PATTERNS:
                            if re.search(pattern, line, re.IGNORECASE):
                                findings.append(
                                    f"  {f.relative_to(f.parents[len(f.parts) - len(scan_dir.parts) - 1])}:{i} — {description}"
                                )
                                break
                except Exception:
                    pass

    return len(findings) == 0, findings


def hard_fail_check(scan_dirs: list[Path]) -> tuple[bool, list[str]]:
    """
    Critic Check 3: Prüft ob hard_fail.py Funktionen korrekt eingebunden sind
    bei Funktionen die Daten aus externen Quellen laden.
    """
    issues = []

    # Muster für Funktionen die I/O machen ohne real_or_die Absicherung
    io_patterns = [
        r'requests\.(get|post|put|delete|patch)\(',
        r'httpx\.(get|post|put|delete)\(',
        r'db\.(query|execute|fetchall|fetchone)\(',
        r'cursor\.(execute|fetchall|fetchone)\(',
        r'await\s+fetch\(',
        r'axios\.(get|post|put|delete)\(',
    ]
    protection_patterns = [
        r'real_or_die\(',
        r'assert_real_io\(',
        r'env_or_die\(',
    ]

    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            continue
        for f in scan_dir.rglob("*.py"):
            if is_ignored(f):
                continue
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")
                lines = content.splitlines()
                for i, line in enumerate(lines, 1):
                    for io_pat in io_patterns:
                        if re.search(io_pat, line):
                            # Prüfe ob in der Nähe (±5 Zeilen) eine Schutzfunktion steht
                            context = "\n".join(lines[max(0, i-3):min(len(lines), i+3)])
                            has_protection = any(re.search(p, context) for p in protection_patterns)
                            if not has_protection:
                                issues.append(
                                    f"  {f.name}:{i} — I/O ohne real_or_die() Schutz: {line.strip()[:60]}"
                                )
            except Exception:
                pass

    return len(issues) == 0, issues


def typecheck(system_facts_path: Path) -> tuple[bool, str, str]:
    """
    Critic Check 2: Führt den in SYSTEM_FACTS konfigurierten Typecheck aus.
    Returns: (passed, command_used, output)
    """
    # Typecheck-Befehl aus SYSTEM_FACTS lesen
    typecheck_cmd = None
    if system_facts_path.exists():
        content = system_facts_path.read_text(encoding="utf-8", errors="ignore")
        for line in content.splitlines():
            if "Typecheck:" in line or "typecheck:" in line or "TYPECHECK_CMD" in line:
                # Extrahiere Befehl
                parts = line.split(":", 1)
                if len(parts) > 1:
                    cmd = parts[1].strip().strip("`").strip()
                    if cmd and "{{" not in cmd and "<" not in cmd:
                        typecheck_cmd = cmd
                        break

    if not typecheck_cmd:
        return True, "N/A", "Kein Typecheck in SYSTEM_FACTS konfiguriert — uebersprungen."

    try:
        result = subprocess.run(
            typecheck_cmd, shell=True, capture_output=True, text=True, timeout=60
        )
        passed = result.returncode == 0
        output = result.stdout + result.stderr
        return passed, typecheck_cmd, output[:500]
    except subprocess.TimeoutExpired:
        return False, typecheck_cmd, "TIMEOUT — Typecheck zu langsam (>60s)"
    except Exception as e:
        return False, typecheck_cmd, f"Fehler beim Ausfuehren: {e}"


def print_tag_report(
    mock_passed: bool, mock_findings: list[str],
    hf_passed: bool, hf_issues: list[str],
    tc_passed: bool, tc_cmd: str, tc_output: str,
    slice_name: str = "?"
):
    """Gibt das offizielle TAG-Protokoll-Format aus."""
    overall = mock_passed and hf_passed and tc_passed
    status_line = "✅ COMMIT FREIGEGEBEN" if overall else "❌ HARD-FAIL — COMMIT GESPERRT"

    tc_status = "✅ CLEAN" if tc_passed else "❌ FEHLER"
    if tc_cmd == "N/A":
        tc_status = "⚠️  N/A (nicht konfiguriert)"

    print(f"""
╔══════════════════════════════════════════════════════════╗
║              TAG — TRIPLE-AGENT-GUARD                    ║
║              Slice: {slice_name:<38}║
╠══════════════════════════════════════════════════════════╣
║ BUILDER:  Code fertiggestellt. I/O-Pfad wird geprueft.   ║
╠══════════════════════════════════════════════════════════╣
║ CRITIC:                                                   ║
║   Mock-Scan:   {"✅ CLEAN (" + str(len(mock_findings)) + " Findings)" if mock_passed else "❌ " + str(len(mock_findings)) + " VIOLATIONS!":<42}║
║   Typecheck:   {tc_status:<42}║
║   Hard-Fail:   {"✅ CLEAN (" + str(len(hf_issues)) + " Issues)" if hf_passed else "❌ " + str(len(hf_issues)) + " ISSUES!":<42}║
║   → CRITIC: {"✅ PASS" if (mock_passed and hf_passed and tc_passed) else "❌ HARD-FAIL":<47}║
╠══════════════════════════════════════════════════════════╣
║ SENTINEL: Protokoll-Konformitaet (manuell zu bestätigen) ║
║   §1 Transparenz:     [ ] Prozesse haben Feedback?       ║
║   §2 Revidierbarkeit: [ ] Aktionen rueckgaengig?         ║
║   §3 Offenlegung:     [ ] UI clean, Details per Click?   ║
║   §4 Menschl. Hoheit: [ ] Mensch bestätigt kritisches?   ║
║   §5 REALD-Protokoll: {"✅ Critic-verified" if mock_passed else "❌ Mock gefunden!":<34}║
╠══════════════════════════════════════════════════════════╣
║ STATUS:   {status_line:<50}║
╚══════════════════════════════════════════════════════════╝""")

    if not mock_passed:
        print("\n[CRITIC] Mock-Violations:")
        for f in mock_findings[:10]:
            print(f)
        if len(mock_findings) > 10:
            print(f"  ... und {len(mock_findings) - 10} weitere.")

    if not hf_passed:
        print("\n[CRITIC] Hard-Fail Issues (ungeschuetzter I/O):")
        for issue in hf_issues[:5]:
            print(issue)

    if not tc_passed and tc_cmd != "N/A":
        print(f"\n[CRITIC] Typecheck Output ({tc_cmd}):")
        print(tc_output[:300])

    if not overall:
        print("\n[TAG] ESKALATION: Zurueck zu PHASE 3 (PLAN). Slice neu definieren.")
        print("[TAG] VERBOT: Kein Korrekturversuch ohne neue SPEC-Validierung durch User (§4).\n")


def main():
    parser = argparse.ArgumentParser(description="TAG — Triple-Agent-Guard Checker")
    parser.add_argument("--mock-scan",  action="store_true", help="Nur Mock-Scan")
    parser.add_argument("--hard-fail",  action="store_true", help="Nur Hard-Fail Check")
    parser.add_argument("--typecheck",  action="store_true", help="Nur Typecheck")
    parser.add_argument("--all",        action="store_true", help="Alle Checks (Default)")
    parser.add_argument("--dir",        type=str, default=None,
                        help="Verzeichnis zum Scannen (Default: src,backend,app,api)")
    parser.add_argument("--slice",      type=str, default="?", help="Slice-Name fuer Report")
    args = parser.parse_args()

    root = Path.cwd()

    # Scan-Verzeichnisse bestimmen
    if args.dir:
        scan_dirs = [root / d.strip() for d in args.dir.split(",")]
    else:
        default_dirs = ["src", "backend", "app", "api", "lib", "core"]
        scan_dirs = [root / d for d in default_dirs if (root / d).exists()]
        if not scan_dirs:
            scan_dirs = [root]  # Fallback: ganzes Projekt (ohne Ignore-Paths)

    run_all = args.all or not (args.mock_scan or args.hard_fail or args.typecheck)

    # Checks ausführen
    mock_passed, mock_findings = True, []
    hf_passed, hf_issues = True, []
    tc_passed, tc_cmd, tc_output = True, "N/A", ""

    if run_all or args.mock_scan:
        print("[TAG] Starte Mock-Scan...")
        mock_passed, mock_findings = mock_scan(scan_dirs)

    if run_all or args.hard_fail:
        print("[TAG] Starte Hard-Fail Check...")
        hf_passed, hf_issues = hard_fail_check(scan_dirs)

    if run_all or args.typecheck:
        system_facts = root / "docs/_rb/02_SYSTEM_FACTS.md"
        print("[TAG] Starte Typecheck...")
        tc_passed, tc_cmd, tc_output = typecheck(system_facts)

    # Report ausgeben
    print_tag_report(
        mock_passed, mock_findings,
        hf_passed, hf_issues,
        tc_passed, tc_cmd, tc_output,
        slice_name=args.slice
    )

    # Exit-Code: 0 = alles grün, 1 = HARD-FAIL
    overall = mock_passed and hf_passed and tc_passed
    sys.exit(0 if overall else 1)


if __name__ == "__main__":
    main()
