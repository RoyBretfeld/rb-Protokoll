#!/usr/bin/env python3
"""
RB-Framework Compare Projects (v3.0)
Vergleicht zwei Verzeichnisse (oder Verzeichnis vs. ZIP) und zeigt Unterschiede.

Usage:
    python compare_projects.py <pfad_a> <pfad_b_oder_zip>

Beispiele:
    python compare_projects.py ./projekt_alt ./projekt_neu
    python compare_projects.py ./lokal ./backup-2026-01-01.zip
"""
import os
import sys
import zipfile
import tempfile
import hashlib
from pathlib import Path


def get_file_hash(filepath) -> str | None:
    """Calculate MD5 hash of a file."""
    hash_md5 = hashlib.md5()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception:
        return None


def scan_directory(directory) -> dict:
    """Scan directory and return dict of relative_path -> {size, hash, mtime}."""
    file_map = {}
    directory = Path(directory)
    for root, _, files in os.walk(directory):
        for file in files:
            full_path = Path(root) / file
            rel_path = full_path.relative_to(directory).as_posix()

            # Skip .git and build artifacts
            parts = rel_path.split("/")
            if any(p in {".git", "__pycache__", "node_modules", ".venv"} for p in parts):
                continue

            try:
                stat = full_path.stat()
                file_map[rel_path] = {
                    "size": stat.st_size,
                    "hash": get_file_hash(full_path),
                    "mtime": stat.st_mtime
                }
            except Exception as e:
                print(f"  [ERR] Error scanning {rel_path}: {e}")
    return file_map


def compare_and_report(files_a: dict, files_b: dict, label_a: str = "A", label_b: str = "B"):
    """Compare two file maps and print a structured diff report."""
    all_files = set(files_a.keys()) | set(files_b.keys())

    added = []    # in A only
    removed = []  # in B only
    modified = []

    for f in all_files:
        in_a = f in files_a
        in_b = f in files_b

        if in_a and not in_b:
            added.append(f)
        elif in_b and not in_a:
            removed.append(f)
        else:
            if files_a[f]["hash"] != files_b[f]["hash"]:
                modified.append(f)

    print("\n" + "=" * 60)
    print("  COMPARISON REPORT")
    print("=" * 60)
    print(f"  {label_a}: {len(files_a)} files")
    print(f"  {label_b}: {len(files_b)} files")

    if modified:
        print(f"\n[MODIFIED] Content changed ({len(modified)}):")
        for f in sorted(modified):
            print(f"  * {f}")

    if added:
        print(f"\n[{label_a} ONLY] Missing in {label_b} ({len(added)}):")
        for f in sorted(added):
            print(f"  + {f}")

    if removed:
        print(f"\n[{label_b} ONLY] Missing in {label_a} ({len(removed)}):")
        for f in sorted(removed):
            print(f"  - {f}")

    if not modified and not added and not removed:
        print("\n  [OK] Identical content – no differences found!")

    print("=" * 60)


def main():
    if len(sys.argv) < 3:
        print("[INFO] RB Compare Projects v3.0")
        print()
        print("Usage:")
        print("  python compare_projects.py <pfad_a> <pfad_b_oder_zip>")
        print()
        print("Beispiele:")
        print("  python compare_projects.py ./projekt_alt ./projekt_neu")
        print("  python compare_projects.py ./lokal ./backup.zip")
        sys.exit(1)

    path_a = Path(sys.argv[1])
    path_b = Path(sys.argv[2])

    if not path_a.exists():
        print(f"[ERR] Pfad A nicht gefunden: {path_a}")
        sys.exit(1)
    if not path_b.exists():
        print(f"[ERR] Pfad B nicht gefunden: {path_b}")
        sys.exit(1)

    print("[INFO] RB Compare Projects v3.0")
    print(f"  A: {path_a}")
    print(f"  B: {path_b}")

    print("\nScanning A...")
    files_a = scan_directory(path_a)

    # B kann ein Verzeichnis oder eine ZIP-Datei sein
    if path_b.suffix.lower() == ".zip":
        with tempfile.TemporaryDirectory() as temp_dir:
            print("Extracting B (zip)...")
            try:
                with zipfile.ZipFile(path_b, "r") as zip_ref:
                    zip_ref.extractall(temp_dir)
            except Exception as e:
                print(f"[ERR] ZIP-Extraktion fehlgeschlagen: {e}")
                sys.exit(1)

            # Verschachtelten Top-Level-Ordner in ZIP erkennen
            extracted_items = os.listdir(temp_dir)
            if len(extracted_items) == 1 and os.path.isdir(os.path.join(temp_dir, extracted_items[0])):
                compare_root = os.path.join(temp_dir, extracted_items[0])
                print(f"  → Verschachtelter ZIP-Ordner erkannt: {extracted_items[0]}")
            else:
                compare_root = temp_dir

            print("Scanning B (zip)...")
            files_b = scan_directory(compare_root)
            compare_and_report(files_a, files_b, label_a="Lokal", label_b="ZIP")
    else:
        print("Scanning B...")
        files_b = scan_directory(path_b)
        compare_and_report(files_a, files_b, label_a="A", label_b="B")


if __name__ == "__main__":
    main()
