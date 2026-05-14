#!/usr/bin/env python3
"""
RB-Framework Police (v3.0 - Hardened)
- Mode: Staged files check (git diff --cached) for pre-commit
- Security: Expanded patterns & blocked files
- Logic: Migration consistency enforce
"""
import os
import re
import sys
import subprocess
from pathlib import Path
from typing import Set, Optional

# === CONFIGURATION ===

# Files that must NEVER be committed
BLOCK_FILES = [
    r"^\.env$", r"\.pem$", r"\.key$", r"\.sqlite$", r"\.db$", 
    r"traffic\.db", r"_DUMP_.*\.md", r".*\.dump$", r".*\.tar\.gz$"
]

# Patterns causing immediate failure if found in code
SECRET_PATTERNS = [
    r"BEGIN (RSA|EC|OPENSSH|DSA) PRI" + r"VATE KEY",
    r"Authorization:\s*Bearer\s+[A-Za-z0-9\-._~+/]{8,}=*",
    # Specific keys: Allow unquoted (common in .ini/.env) OR quoted
    r"(jwt_secret|openai_api_key|aws_access_key_id|auth_token)\s*[=:]\s*(\S{8,}|['\"][^'\"]{8,}['\"])",
    # Generic keys: REQUIRE quotes to avoid false positives in code
    r"(api[_-]?key|token|password|secret|database_url|smtp_password)\s*[=:]\s*['\"][^'\"]{8,}['\"]",
    r"post" + r"gres://.*:.*@",
    r"my" + r"sql://.*:.*@",
]

# Files to scan for content (text-based)
SCAN_EXT = {
    ".py", ".js", ".ts", ".html", ".css", ".md", ".sql", 
    ".yml", ".yaml", ".json", ".toml", ".xml", ".sh", ".ini", ".env.example"
}

# Ignore these lines during scan to reduce false positives
SAFE_LINE_PATTERNS = [
    r"^\s*#",           # Comments
    r"^\s*//", 
    r"^\s*\*",
    r"{{.*}}",          # Placeholders
    r"YOUR_API_KEY",    # Examples
    r"example\.com", 
    r"TODO|FIXME"
]

# Migration Rules
SCHEMA_PATTERN = r"db/schema\.(sql|prisma|xml|py)$"
MIGRATION_DIR = "db/migrations"

def fail(msg: str):
    print(f"[POLICE] ❌ FAIL: {msg}", file=sys.stderr)
    sys.exit(1)

def get_staged_files() -> Optional[Set[Path]]:
    """Get only files staged for commit."""
    try:
        # Check if inside git tree
        subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], 
                      capture_output=True, check=True)
        
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
            capture_output=True, text=True, check=True
        )
        files = {Path(f) for f in result.stdout.strip().split("\n") if f}
        return files
    except subprocess.CalledProcessError:
        return None

def get_all_files(root: Path) -> Set[Path]:
    """Fallback: Scan all files if not in git."""
    all_files = set()
    for ext in SCAN_EXT:
        all_files.update(root.rglob(f"*{ext}"))
    return {f for f in all_files if ".git" not in f.parts and "_archive" not in f.parts}

def is_safe_line(line: str) -> bool:
    return any(re.search(pat, line, re.IGNORECASE) for pat in SAFE_LINE_PATTERNS)

def scan_file(path: Path):
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return # Skip binary/unreadable

    for i, line in enumerate(content.split("\n"), start=1):
        if is_safe_line(line):
            continue
        for pattern in SECRET_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                # Obfuscate output
                clean_line = line.strip()[:60]
                fail(f"Secret pattern match in {path}:{i}\n    Line: {clean_line}...\n    Pattern: {pattern}")

def check_migration_consistency(files: Set[Path]):
    # Convert to posix strings for regex matching
    file_strs = {str(f).replace("\\", "/") for f in files}
    
    schema_changed = any(re.search(SCHEMA_PATTERN, f) for f in file_strs)
    migration_touched = any(MIGRATION_DIR in f for f in file_strs)

    if schema_changed and not migration_touched:
        fail(f"Schema drift detected!\n    Changed: db/schema.*\n    Missing: {MIGRATION_DIR}/*\n    Rule: Schema changes must be accompanied by a new migration.")

def check_verify_phase():
    """SENTINEL RULE: Block commit if SPEC exists but VERIFY is not documented."""
    planning_dir = Path.cwd() / ".planning"
    requirements = planning_dir / "requirements.md"
    roadmap = planning_dir / "roadmap.md"

    if not requirements.exists():
        return  # No spec-driven project, skip

    # Check if requirements.md has at least one non-template entry
    req_content = requirements.read_text(encoding="utf-8", errors="ignore")
    has_spec = bool(re.search(r"^## \[?(?!Feature-Name)", req_content, re.MULTILINE))
    if not has_spec:
        return  # Only template content, no real spec yet

    if not roadmap.exists():
        fail("SENTINEL RULE: .planning/requirements.md has active specs but .planning/roadmap.md is missing.\n"
             "    Rule: Document VERIFY phase before committing.")

    roadmap_content = roadmap.read_text(encoding="utf-8", errors="ignore")
    # Check for a VERIFY section with a completion marker
    has_verify_done = bool(re.search(r"##\s+VERIFY.*\n(?:.*\n)*?.*Status:\s*(✅|DONE)", roadmap_content))
    if not has_verify_done:
        fail("SENTINEL RULE: Active specs in .planning/requirements.md detected, but no completed VERIFY "
             "section found in .planning/roadmap.md.\n"
             "    Required: '## VERIFY' section with 'Status: ✅ DONE'\n"
             "    Rule: No merge without documented Verify phase.")

def check_system_facts():
    """SENTINEL RULE: Block commit if SYSTEM_FACTS is missing or has unresolved placeholders."""
    facts_file = Path("docs/_rb/02_SYSTEM_FACTS.md")
    if not facts_file.exists():
        fail("SENTINEL RULE: docs/_rb/02_SYSTEM_FACTS.md not found.\n"
             "    Rule: SYSTEM_FACTS must exist before any commit.")

    try:
        content = facts_file.read_text(encoding="utf-8")
    except OSError as e:
        fail(f"SENTINEL RULE: Cannot read SYSTEM_FACTS: {e}\n"
             "    Rule: SYSTEM_FACTS must be readable.")

    unfilled = re.findall(r'\{\{([^}]+)\}\}', content)
    if unfilled:
        placeholders = ", ".join(f"{{{{ {p} }}}}" for p in unfilled[:5])
        suffix = f" ... and {len(unfilled) - 5} more" if len(unfilled) > 5 else ""
        fail(f"SENTINEL RULE: {len(unfilled)} unresolved placeholder(s) in SYSTEM_FACTS:\n"
             f"    {placeholders}{suffix}\n"
             "    Rule: All placeholders must be filled before committing.")


def main():
    print("[POLICE] 🛡️  Starting Security & Consistency Check...")
    
    staged = get_staged_files()
    
    if staged is not None:
        print(f"[POLICE] ℹ️  Git staged mode: Scanning {len(staged)} files.")
        target_files = {f for f in staged if f.exists() and "_archive" not in f.parts and "Export-rb-Protokoll" not in f.parts}
        # Verify migration consistency on the changeset
        check_migration_consistency(target_files)
    else:
        print("[POLICE] ⚠️  Not a git repo or no git access. Performing FULL scan.")
        target_files = get_all_files(Path.cwd())

    # 0. SENTINEL RULE: Verify phase check
    check_verify_phase()

    # 0b. SENTINEL RULE: SYSTEM_FACTS existence and placeholder check
    check_system_facts()

    # 1. Check for blocked filenames
    for f in target_files:
        path_str = str(f).replace("\\", "/")
        if "_archive" in f.parts:
            continue
        for block in BLOCK_FILES:
            if re.search(block, f.name, re.IGNORECASE):
                fail(f"Forbidden file blocked: {f}")

    # 2. content scan
    scannable = {f for f in target_files if f.suffix in SCAN_EXT}
    for f in scannable:
        scan_file(f)

    print("[POLICE] ✅ All checks passed.")

if __name__ == "__main__":
    main()
