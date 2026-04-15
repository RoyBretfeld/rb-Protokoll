#!/usr/bin/env python3
"""
RB-Framework CLI (v2.0)
Unified command interface for check/test/pack/learn
"""
import argparse
import subprocess
import sys
import re
from pathlib import Path

def has_placeholder(cmd: str) -> bool:
    """Check if command still contains {{PLACEHOLDER}}."""
    return bool(re.search(r'\{\{[^}]+\}\}', cmd))

def parse_system_facts() -> dict[str, str]:
    """Parse key-value pairs from docs/_rb/02_SYSTEM_FACTS.md.

    Reads lines matching '- Key: value' and returns them as a dict.
    Lines where value starts with '<!--' (HTML comments) are skipped.
    """
    facts_file = Path("docs/_rb/02_SYSTEM_FACTS.md")
    if not facts_file.exists():
        return {}

    content = facts_file.read_text(encoding="utf-8")
    facts: dict[str, str] = {}

    for line in content.splitlines():
        m = re.match(r'^-\s+([^:]+):\s*(.+)$', line.strip())
        if m:
            key = m.group(1).strip()
            value = m.group(2).strip()
            if value and not value.startswith('<!--'):
                facts[key] = value

    return facts

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
        print(f"❌ HARD-FAIL: {len(unfilled)} unresolved placeholder(s) in SYSTEM_FACTS:", file=sys.stderr)
        for placeholder in unfilled[:5]:  # Show first 5
            print(f"   - {{{{ {placeholder} }}}}", file=sys.stderr)
        if len(unfilled) > 5:
            print(f"   ... and {len(unfilled) - 5} more", file=sys.stderr)
        print("\n💡 Fill placeholders in docs/_rb/02_SYSTEM_FACTS.md before proceeding.\n", file=sys.stderr)
        return False

    return True

def main():
    p = argparse.ArgumentParser(
        prog="rb",
        description="RB-Framework unified CLI",
        epilog="See docs/_rb/ for full documentation"
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
        # SYSTEM_FACTS validation (must pass before anything else)
        if not check_system_facts():
            sys.exit(1)
        # Police (always runs, no placeholders)
        if run("python scripts/pre_commit_police.py") != 0:
            sys.exit(1)
        
        # Baseline tests (parsed from SYSTEM_FACTS)
        facts = parse_system_facts()
        baseline_cmd = facts.get("Baseline", "")
        if not baseline_cmd or has_placeholder(baseline_cmd):
            print("⚠️  No baseline tests configured (Baseline not set in SYSTEM_FACTS)")
            print("✅ Police check passed - assuming OK")
            sys.exit(0)
        
        if run(baseline_cmd) != 0:
            sys.exit(1)
        
        print("\n✅ All checks passed!")
        sys.exit(0)

    if a.cmd == "test":
        print("🧪 Running full test suite...\n")
        facts = parse_system_facts()
        test_cmd = facts.get("Full tests", "")
        if not test_cmd or has_placeholder(test_cmd):
            print("❌ ERROR: Full tests command not configured in SYSTEM_FACTS", file=sys.stderr)
            print("💡 Set 'Full tests:' in docs/_rb/02_SYSTEM_FACTS.md", file=sys.stderr)
            sys.exit(1)
        sys.exit(run(test_cmd))

    if a.cmd == "pack":
        print("📦 Generating project context dump...\n")
        sys.exit(run("python scripts/packer.py"))

    if a.cmd == "learn":
        template_file = Path(r"E:\_____1111____Projekte-Programmierung\Antigravity\03_ERROR_DB.md")
        if not template_file.exists():
            print(f"❌ ERROR: Central Error-DB not found at {template_file}!", file=sys.stderr)
            sys.exit(1)
        
        print("📝 Create a new Error-DB entry:")
        print(f"   Edit: {template_file}")
        print("\nTemplate:")
        print("- ID: ERR-YYYYMMDD-SHORT")
        print("- Symptom: What went wrong?")
        print("- Root Cause: Why did it happen?")
        print("- Fix: How was it resolved?")
        print("- Regression Test: How to prevent recurrence?")
        print("- Prevention Rule: New guardrail?")
        sys.exit(0)

if __name__ == "__main__":
    main()

