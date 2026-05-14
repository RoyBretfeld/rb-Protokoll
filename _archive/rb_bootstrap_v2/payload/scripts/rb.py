#!/usr/bin/env python3
"""
RB-Framework CLI (v2.1)
Unified command interface for check/test/pack/learn
Integrates 4 Laws & External Error DB
"""
import argparse
import subprocess
import sys
import re
from pathlib import Path

def has_placeholder(cmd: str) -> bool:
    """Check if command still contains {{PLACEHOLDER}}."""
    return bool(re.search(r'\{\{[^}]+\}\}', cmd))

def get_error_db_path() -> Path:
    """Resolve Error DB path from SYSTEM_FACTS or default."""
    facts_file = Path("docs/_rb/02_SYSTEM_FACTS.md")
    default_path = Path("docs/_rb/03_ERROR_DB.md")
    
    if not facts_file.exists():
        return default_path
        
    content = facts_file.read_text(encoding="utf-8")
    # Search for Error DB path in markdown link or text
    # Expected format: **Error DB**: `../../03_ERROR_DB.md`
    match = re.search(r'\*\*Error DB\*\*: `([^`]+)`', content)
    if match:
        rel_path = match.group(1)
        # Resolve relative to docs/_rb/ where SYSTEM_FACTS lives
        # But we run from root, so we need to be careful.
        # scripts/rb.py runs from project root.
        # docs/_rb/02_SYSTEM_FACTS.md is in docs/_rb/
        # relative path ../../03_ERROR_DB.md from docs/_rb/ points to root/03_ERROR_DB.md
        
        base_dir = Path("docs/_rb")
        resolved = (base_dir / rel_path).resolve()
        
        # Try to return relative to CWD for cleaner output if possible
        try:
            return resolved.relative_to(Path.cwd())
        except ValueError:
            return resolved
            
    return default_path

def run(cmd: str, allow_placeholder: bool = False) -> int:
    """Execute shell command with validation."""
    if not allow_placeholder and has_placeholder(cmd):
        print(f"\n❌ ERROR: Command contains unfilled placeholder(s):", file=sys.stderr)
        print(f"   {cmd}", file=sys.stderr)
        print(f"\n💡 Fix: Update docs/_rb/02_SYSTEM_FACTS.md and regenerate rb.py", file=sys.stderr)
        return 1
    
    print(f"\n$ {cmd}")
    try:
        return subprocess.call(cmd, shell=True)
    except KeyboardInterrupt:
        print("\n⚠️  Command interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ Command failed: {e}", file=sys.stderr)
        return 1

def check_system_facts() -> bool:
    """Verify SYSTEM_FACTS exists and is filled out."""
    facts_file = Path("docs/_rb/02_SYSTEM_FACTS.md")
    if not facts_file.exists():
        print("❌ ERROR: docs/_rb/02_SYSTEM_FACTS.md not found!", file=sys.stderr)
        return False
    
    content = facts_file.read_text(encoding="utf-8")
    unfilled = re.findall(r'\{\{([^}]+)\}\}', content)
    
    if unfilled:
        print(f"⚠️  WARNING: {len(unfilled)} placeholder(s) in SYSTEM_FACTS:", file=sys.stderr)
        for placeholder in unfilled[:5]:  # Show first 5
            print(f"   - {{{{ {placeholder} }}}}", file=sys.stderr)
        if len(unfilled) > 5:
            print(f"   ... and {len(unfilled) - 5} more", file=sys.stderr)
        print("\n💡 Run the agent initialization task to fill these out.\n", file=sys.stderr)
    
    return True

def main():
    p = argparse.ArgumentParser(
        prog="rb",
        description="RB-Framework unified CLI v2.1",
        epilog="See docs/_rb/ for 4 Laws and full documentation"
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    # Commands
    sub.add_parser("check", help="Run police + baseline tests (pre-commit gate)")
    sub.add_parser("test", help="Run full test suite")
    sub.add_parser("pack", help="Generate context dump for agents/debug")
    sub.add_parser("learn", help="Create new Error-DB entry")
    sub.add_parser("init", help="Verify RB-Framework setup")

    a = p.parse_args()

    # Location check
    if not Path("docs/_rb/00_BOOT_PROTOCOL.md").exists():
        print("❌ ERROR: Not in RB-Framework root directory!", file=sys.stderr)
        print("   Expected docs/_rb/00_BOOT_PROTOCOL.md to exist", file=sys.stderr)
        sys.exit(1)

    # === COMMANDS ===
    
    if a.cmd == "init":
        print("🔍 Checking RB-Framework setup...\n")
        if check_system_facts():
            print("✅ RB-Framework is properly initialized")
            sys.exit(0)
        else:
            sys.exit(1)

    if a.cmd == "check":
        print("🚓 Running pre-commit checks...\n")
        
        # 1. Check Error DB existence (Law #1 & #2 Support)
        error_db = get_error_db_path()
        if not error_db.exists():
            print(f"❌ ERROR: Error DB not found at: {error_db}", file=sys.stderr)
            print("   Required for core law compliance (Transparency/Reversibility).", file=sys.stderr)
            sys.exit(1)
        else:
            print(f"✅ Error DB found at: {error_db}")

        # 2. Run Police (if exists)
        if Path("scripts/pre_commit_police.py").exists():
            if run("python scripts/pre_commit_police.py") != 0:
                sys.exit(1)
        else:
            print("ℹ️  No police script found, skipping.")
        
        # 3. Baseline tests (may have placeholders in templates, usually user replaces them)
        # For this setup, we assume manual config or simple pass if not configured
        baseline_cmd = "{{BASELINE_TEST_CMD}}"
        if has_placeholder(baseline_cmd):
            print("ℹ️  No baseline tests configured (BASELINE_TEST_CMD not set)")
        else:
            if run(baseline_cmd) != 0:
                sys.exit(1)
        
        print("\n✅ All checks passed! (4 Laws Compliant)")
        sys.exit(0)

    if a.cmd == "test":
        print("🧪 Running full test suite...\n")
        test_cmd = "{{FULL_TEST_CMD}}"
        if has_placeholder(test_cmd):
            print("⚠️  No full tests configured.")
            sys.exit(0)
        sys.exit(run(test_cmd))

    if a.cmd == "pack":
        print("📦 Generating project context dump...\n")
        if Path("scripts/packer.py").exists():
            sys.exit(run("python scripts/packer.py"))
        else:
            print("❌ scripts/packer.py missing!")
            sys.exit(1)

    if a.cmd == "learn":
        error_db = get_error_db_path()
        if not error_db.exists():
            print(f"❌ ERROR: Error-DB not found at {error_db}!", file=sys.stderr)
            sys.exit(1)
        
        print("📝 Create a new Error-DB entry:")
        print(f"   Edit: {error_db}")
        print("\nTemplate (append to file):")
        print("- ID: ERR-YYYYMMDD-SHORT")
        print("- Symptom: What went wrong?")
        print("- Root Cause: Why did it happen?")
        print("- Fix: How was it resolved?")
        print("- Regression Test: How to prevent recurrence?")
        print("- Prevention Rule: New guardrail?")
        sys.exit(0)

if __name__ == "__main__":
    main()

