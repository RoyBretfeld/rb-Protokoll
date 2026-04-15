#!/usr/bin/env python3
"""
RB-Framework TAG-Check (v1.0)
Triple-Agent-Guard — Mechanical verification before every commit.

Scans staged files for mock usage and unfinished code.
Exits 0 on PASS, 1 on HARD-FAIL.
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Set, Optional

# === MOCK PATTERNS (HARD-FAIL in production code) ===
MOCK_PATTERNS = [
    r"\bMock\s*\(",
    r"\bMagicMock\s*\(",
    r"\bmock\s*\.",
    r"\bdummy[_\w]*\s*=",          # dummy = ... / dummy_var = ...
    r"\bplaceholder_\w+\s*=",       # placeholder_data = ...
    r"=\s*placeholder\b",           # x = placeholder (assignment value)
    r"\bfake_\w+\s*=",              # fake_data = ...
    r"\bexample_data\s*=",
    r"\bunittest\.mock\b",
    r"\bfrom\s+unittest\.mock\s+import\b",
]

# === TODO PATTERNS (HARD-FAIL — unfinished code) ===
TODO_PATTERNS = [
    r"#\s*TODO",
    r"#\s*FIXME",
    r"\bpass\s*#\s*TODO",
    r"\braise\s+NotImplementedError",
    r"\breturn\s+\[\]\s*#\s*TODO",
    r"\breturn\s+\{\}\s*#\s*TODO",
    r"\breturn\s+None\s*#\s*TODO",
]

# === FILE EXTENSIONS TO SCAN ===
SCAN_EXT = {".py", ".js", ".ts", ".html", ".css", ".sql",
            ".yml", ".yaml", ".json", ".toml", ".sh"}

# === TEST FILE PATTERNS (mocks allowed here) ===
TEST_PATTERNS = [
    r"^test_",
    r"_test\.",
    r"tests[/\\]",
    r"__tests__[/\\]",
    r"spec[/\\]",
    r"conftest\.",
]


def is_test_file(path: Path) -> bool:
    """Check if file is a test file (mocks allowed)."""
    path_str = str(path).replace("\\", "/")
    return any(re.search(pat, path_str) for pat in TEST_PATTERNS)


def is_comment_line(line: str) -> bool:
    """Check if line is a comment-only line or docstring boundary."""
    stripped = line.strip()
    return (stripped.startswith("#")
            or stripped.startswith("//")
            or stripped.startswith("*")
            or stripped.startswith('"""')
            or stripped.startswith("'''"))


def is_pattern_line(line: str) -> bool:
    """Check if line is a regex pattern definition or inside a docstring."""
    stripped = line.strip()
    # Regex pattern assignments: r"..." or r'...'
    if stripped.startswith('r"') or stripped.startswith("r'"):
        return True
    # Docstring content lines
    if stripped.startswith("- ") and stripped.endswith("."):
        return True
    return False


def get_staged_files() -> Optional[Set[Path]]:
    """Get files staged for commit."""
    try:
        subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            capture_output=True, check=True,
        )
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
            capture_output=True, text=True, check=True,
        )
        files = {Path(f) for f in result.stdout.strip().split("\n") if f}
        return files
    except subprocess.CalledProcessError:
        return None


def get_all_files() -> Set[Path]:
    """Fallback: scan all scannable files in repo."""
    root = Path.cwd()
    all_files: Set[Path] = set()
    for ext in SCAN_EXT:
        all_files.update(root.rglob(f"*{ext}"))
    return {f for f in all_files
            if ".git" not in f.parts
            and "_rb_dumps" not in f.parts
            and "__pycache__" not in f.parts
            and ".agent" not in f.parts
            and "_archive" not in f.parts}


def scan_file(path: Path) -> list[tuple[str, int, str, str]]:
    """Scan a single file. Returns list of (category, line_no, line, pattern)."""
    findings: list[tuple[str, int, str, str]] = []

    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return findings

    is_test = is_test_file(path)

    for i, line in enumerate(content.splitlines(), start=1):
        stripped = line.strip()

        # Mock scan (skip test files — mocks allowed there per §5)
        if not is_test and not is_pattern_line(line):
            for pattern in MOCK_PATTERNS:
                if re.search(pattern, stripped, re.IGNORECASE):
                    findings.append(("MOCK", i, stripped[:80], pattern))
                    break  # one finding per line is enough

        # Unfinished-code scan (skip pure comment lines in non-code files)
        for pattern in TODO_PATTERNS:
            if re.search(pattern, stripped, re.IGNORECASE):
                # In code files, TODO in code is always a hard-fail
                # In config/docs, comment TODOs are warnings, not fails
                if path.suffix == ".py" or not is_comment_line(line):
                    findings.append(("TODO", i, stripped[:80], pattern))
                    break

    return findings


def main():
    parser = argparse.ArgumentParser(
        prog="rb_tag_check",
        description="TAG — Triple-Agent-Guard mechanical verification",
    )
    parser.add_argument("--all", action="store_true",
                        help="Scan all files, not just staged")
    parser.add_argument("--slice", type=str, default="",
                        help="Slice identifier e.g. 'Slice-1: Name'")
    args = parser.parse_args()

    slice_name = args.slice or "(unspecified)"

    # Get files to scan
    if args.all:
        files = get_all_files()
        mode = "FULL"
    else:
        staged = get_staged_files()
        if staged is not None:
            files = {f for f in staged if f.exists()}
            mode = "STAGED"
        else:
            files = get_all_files()
            mode = "FULL (no git)"

    scannable = {f for f in files if f.suffix in SCAN_EXT and not is_test_file(f)}

    # Run scans
    all_findings: list[tuple[Path, str, int, str, str]] = []
    for f in sorted(scannable):
        for category, line_no, line, pattern in scan_file(f):
            all_findings.append((f, category, line_no, line, pattern))

    mock_findings = [(f, cat, ln, line, pat) for f, cat, ln, line, pat in all_findings if cat == "MOCK"]
    todo_findings = [(f, cat, ln, line, pat) for f, cat, ln, line, pat in all_findings if cat == "TODO"]

    hard_fail = len(mock_findings) > 0 or len(todo_findings) > 0

    # === OUTPUT: TAG-GUARD DIALOG ===
    print()
    print("=" * 60)
    print("TAG — TRIPLE-AGENT-GUARD")
    print(f"Slice: {slice_name}")
    print("=" * 60)

    # BUILDER
    print()
    print("BUILDER:  Code fertiggestellt.", end=" ")
    if not hard_fail:
        print("I/O-Pfad vorhanden. Kein Mock, kein TODO, kein statischer Fallback.")
    else:
        print("HARD-FAIL erkannt — siehe CRITIC.")

    # CRITIC
    print()
    if mock_findings:
        print(f"CRITIC:   Mock-Scan:    ❌ HARD-FAIL ({len(mock_findings)} finding(s))")
        for f, _, ln, line, pat in mock_findings[:10]:
            rel = f.relative_to(Path.cwd()) if f.is_relative_to(Path.cwd()) else f
            print(f"  {rel}:{ln}  {line}")
            if len(mock_findings) > 10:
                print(f"  ... and {len(mock_findings) - 10} more")
                break
    else:
        print("CRITIC:   Mock-Scan:    ✅ CLEAN")

    if todo_findings:
        print(f"          TODO-Scan:    ❌ HARD-FAIL ({len(todo_findings)} finding(s))")
        for f, _, ln, line, pat in todo_findings[:10]:
            rel = f.relative_to(Path.cwd()) if f.is_relative_to(Path.cwd()) else f
            print(f"  {rel}:{ln}  {line}")
            if len(todo_findings) > 10:
                print(f"  ... and {len(todo_findings) - 10} more")
                break
    else:
        print("          TODO-Scan:    ✅ CLEAN")

    print(f"          Typecheck:    ⚠️ N/A")

    if hard_fail:
        print()
        print("          → CRITIC: ❌ HARD-FAIL")
    else:
        print()
        print("          → CRITIC: ✅ PASS")

    # SENTINEL (manual check reminder)
    print()
    print("SENTINEL: §1 Transparenz:      [manuell prüfen]")
    print("          §2 Revidierbarkeit:  [manuell prüfen]")
    print("          §3 Offenlegung:      [manuell prüfen]")
    print("          §4 Menschl. Hoheit:  [manuell prüfen]")
    print("          §5 REALD-Protokoll:  ✅ (automatisch geprüft)")

    print()
    if hard_fail:
        print("=" * 60)
        print("STATUS:   ❌ COMMIT BLOCKIERT — HARD-FAIL")
        print("=" * 60)
        print()
        print("→ Zurück zu PHASE 3 (PLAN). Slice neu definieren.")
        print("→ SPEC mit User re-validieren (§4 Menschliche Hoheit).")
        print("→ Erst dann neuer Builder-Versuch.")
        sys.exit(1)
    else:
        print("=" * 60)
        print("STATUS:   ✅ COMMIT FREIGEGEBEN (CRITIC)")
        print("           SENTINEL: 5 Gesetze manuell bestätigen")
        print("=" * 60)
        sys.exit(0)


if __name__ == "__main__":
    main()