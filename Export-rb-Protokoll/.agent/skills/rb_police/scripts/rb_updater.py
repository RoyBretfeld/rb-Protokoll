#!/usr/bin/env python3
"""
rb_updater.py — RB-Protokoll Update-Tool
Version: 1.0.0 | RB-Framework (Antigravity Edition)

ZWECK:
    Aktualisiert das RB-Protokoll in einem bestehenden Projekt
    auf den neusten Stand des Export-Pakets — ohne projekt-spezifische
    Dateien anzutasten.

VERWENDUNG:
    # Dry-Run (zeigt was geändert würde, ändert nichts):
    python rb_updater.py --source <EXPORT_PFAD> --target <PROJEKT_PFAD>

    # Update ausführen (nach Bestätigung):
    python rb_updater.py --source <EXPORT_PFAD> --target <PROJEKT_PFAD> --apply

    # Force (ohne Bestätigungsdialog — für Automation):
    python rb_updater.py --source <EXPORT_PFAD> --target <PROJEKT_PFAD> --apply --force

STANDARD-QUELLE (wenn --source fehlt):
    E:\\_____1111____Projekte-Programmierung\\Antigravity\\_rb-Protokoll\\Export-rb-Protokoll

REGELN:
    §2 Revidierbarkeit: Vor jedem Update wird ein Backup nach _archive/ erstellt.
    §4 Menschliche Hoheit: Dry-Run ist Default, --apply muss explizit angegeben werden.
"""

import sys
import shutil
import hashlib
import argparse
from pathlib import Path
from datetime import datetime

# Fix Windows UnicodeEncodeError (ERR-20260309-WIN-EMOJI)
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# ──────────────────────────────────────────────
# WHITELIST: Diese Dateien darf der Updater anfassen
# (Protokoll-Core — kein Projekt-spezifischer Inhalt)
# ──────────────────────────────────────────────
UPDATABLE_FILES = [
    # Skills (nur SKILL.md, keine scripts/ — außer police)
    ".agent/skills/rb_bootstrap/SKILL.md",
    ".agent/skills/rb_police/SKILL.md",
    ".agent/skills/rb_police/scripts/pre_commit_police.py",
    ".agent/skills/rb_police/scripts/hard_fail.py",
    ".agent/skills/rb_police/scripts/rb_updater.py",    # Selbst-Update!
    ".agent/skills/rb_packer/SKILL.md",
    ".agent/skills/rb_packer/scripts/packer.py",
    ".agent/skills/ux_guardian/SKILL.md",
    ".agent/skills/error_learner/SKILL.md",
    # Workflows
    ".agent/workflows/bootstrap.md",
    ".agent/workflows/check.md",
    ".agent/workflows/flow-close.md",
    ".agent/workflows/learn.md",
    ".agent/workflows/pack.md",
    ".agent/workflows/sentinelcheck.md",
    # Protokoll-Dokumente (keine project-spezifischen Werte)
    "docs/_rb/00_BOOT_PROTOCOL.md",
    "docs/_rb/01_AGENT_LOOP.md",
    "docs/_rb/01_MISSION_PROMPT.md",
    "docs/_rb/01_PLAN_EXECUTION.md",
    "docs/_rb/04_STANDARDS.md",
    "docs/_rb/04_UX_LAWS.md",
    "docs/_rb/05_SECURITY.md",
    "docs/_rb/06_TEST_MATRIX.md",
    "docs/_rb/BOOTSTRAP_PROMPT.md",
    # Meta
    "PROTOCOL_VERSION",
    "start.md",
]

# ──────────────────────────────────────────────
# BLACKLIST: Diese Dateien werden NIEMALS angefasst
# (Projekt-spezifisch — enthält echte Projekt-Daten)
# ──────────────────────────────────────────────
PROTECTED_FILES = {
    "docs/_rb/02_SYSTEM_FACTS.md",   # Stack, Pfade, Commands — pro Projekt einzigartig
    "docs/_rb/03_ERROR_DB.md",       # Projektspezifische Fehlerhistorie
    ".env",
    ".gitignore",                    # Projekt hat eigene gitignore-Regeln
    "README.md",                     # Projektspezifisch
    "CHANGELOG.md",                  # Projektspezifisch
}


def md5(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def get_protocol_version(directory: Path) -> str:
    version_file = directory / "PROTOCOL_VERSION"
    if version_file.exists():
        return version_file.read_text(encoding="utf-8").split("\n")[0].strip()
    return "UNKNOWN"


def create_backup(target: Path, file_rel: str) -> Path | None:
    """Erstellt ein Backup der Datei in target/_archive/rb_update_DATUM/"""
    target_file = target / file_rel
    if not target_file.exists():
        return None
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = target / "_archive" / f"rb_update_{timestamp}"
    backup_file = backup_dir / file_rel
    backup_file.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(target_file, backup_file)
    return backup_file


def run_update(source: Path, target: Path, apply: bool, force: bool) -> int:
    """
    Hauptlogik:
    1. Versionen vergleichen
    2. Geänderte Dateien ermitteln
    3. Dry-Run oder Apply
    """
    src_version = get_protocol_version(source)
    tgt_version = get_protocol_version(target)

    print(f"\n{'='*60}")
    print(f"  RB-Protokoll Updater v1.0")
    print(f"{'='*60}")
    print(f"  Quelle:  {source}")
    print(f"  Ziel:    {target}")
    print(f"  Quelle-Version: {src_version}")
    print(f"  Projekt-Version: {tgt_version}")
    print(f"  Modus:   {'APPLY' if apply else 'DRY-RUN (kein Schreiben)'}")
    print(f"{'='*60}\n")

    if src_version == tgt_version:
        print(f"[OK] Projekt ist bereits auf Version {tgt_version}. Kein Update noetig.")
        return 0

    # Dateien analysieren
    to_add    = []  # Neu im Protokoll — existiert noch nicht im Projekt
    to_update = []  # Existiert, aber veraltet (MD5 unterschiedlich)
    up_to_date = [] # Existiert und identisch

    for rel_path in UPDATABLE_FILES:
        src_file = source / rel_path
        tgt_file = target / rel_path

        if not src_file.exists():
            continue  # Quelldatei fehlt — überspringen

        if rel_path in PROTECTED_FILES:
            print(f"[PROTECTED] {rel_path} — wird nie angefasst")
            continue

        if not tgt_file.exists():
            to_add.append(rel_path)
        elif md5(src_file) != md5(tgt_file):
            to_update.append(rel_path)
        else:
            up_to_date.append(rel_path)

    # Report
    print(f"  [+] Neu hinzufuegen:  {len(to_add)} Datei(en)")
    for f in to_add:
        print(f"      + {f}")

    print(f"\n  [~] Aktualisieren:    {len(to_update)} Datei(en)")
    for f in to_update:
        print(f"      ~ {f}")

    print(f"\n  [=] Bereits aktuell: {len(up_to_date)} Datei(en)")
    print()

    if not to_add and not to_update:
        print("[OK] Alle Kern-Dateien sind aktuell.")
        return 0

    if not apply:
        print("[DRY-RUN] Keine Aenderungen durchgefuehrt.")
        print(f"          Zum Ausfuehren: --apply hinzufuegen\n")
        return 0

    # §4 Menschliche Hoheit: Bestätigung einholen (wenn nicht --force)
    if not force:
        print(f"BEREIT zum Update von v{tgt_version} auf v{src_version}.")
        print(f"  {len(to_add)} neue + {len(to_update)} geaenderte Dateien.")
        confirm = input("\nUpdate ausfuehren? [j/N]: ").strip().lower()
        if confirm not in ("j", "ja", "y", "yes"):
            print("[ABBRUCH] Kein Update durchgefuehrt.")
            return 0

    # Backup + Apply
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = target / "_archive" / f"rb_update_{timestamp}"
    backed_up = []

    for rel_path in (to_add + to_update):
        src_file = source / rel_path
        tgt_file = target / rel_path

        # Backup (§2 Revidierbarkeit)
        if tgt_file.exists():
            backup_file = backup_dir / rel_path
            backup_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(tgt_file, backup_file)
            backed_up.append(rel_path)

        # Kopieren
        tgt_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_file, tgt_file)
        action = "ADDED" if rel_path in to_add else "UPDATED"
        print(f"  [{action}] {rel_path}")

    # PROTOCOL_VERSION im Projekt setzen
    version_target = target / "PROTOCOL_VERSION"
    shutil.copy2(source / "PROTOCOL_VERSION", version_target)

    print(f"\n{'='*60}")
    print(f"  [OK] Update abgeschlossen!")
    print(f"  Neue Version: {src_version}")
    if backed_up:
        print(f"  Backup:  _archive/rb_update_{timestamp}/")
    print(f"{'='*60}\n")

    return 0


def main():
    DEFAULT_SOURCE = Path(
        r"E:\_____1111____Projekte-Programmierung\Antigravity\_rb-Protokoll\Export-rb-Protokoll"
    )

    parser = argparse.ArgumentParser(
        description="RB-Protokoll Updater — aktualisiert Protokoll-Core-Dateien sicher."
    )
    parser.add_argument(
        "--source", type=Path, default=DEFAULT_SOURCE,
        help=f"Pfad zum Export-rb-Protokoll (Default: {DEFAULT_SOURCE})"
    )
    parser.add_argument(
        "--target", type=Path, default=Path.cwd(),
        help="Pfad zum Zielprojekt (Default: aktuelles Verzeichnis)"
    )
    parser.add_argument(
        "--apply", action="store_true",
        help="Update tatsaechlich durchfuehren (Default: nur Dry-Run)"
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Keine Rueckfrage (fuer Automatisierung). Nur mit --apply."
    )

    args = parser.parse_args()

    if not args.source.exists():
        print(f"[FEHLER] Quell-Verzeichnis nicht gefunden: {args.source}")
        sys.exit(1)

    if not args.target.exists():
        print(f"[FEHLER] Ziel-Verzeichnis nicht gefunden: {args.target}")
        sys.exit(1)

    sys.exit(run_update(args.source, args.target, args.apply, args.force))


if __name__ == "__main__":
    main()
