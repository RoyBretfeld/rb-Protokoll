#!/usr/bin/env python3
"""
RB-Framework Packer - "Der Kleine Bruder" (Structure Mapper) - V2 (Live-Streaming)
Erstellt eine Baumstruktur und schreibt direkt (Live-Update).
Gibt den Fortschritt auf der Konsole aus.
"""
import sys
import time
from pathlib import Path

EXCLUDE_DIRS = {".git", "docs/_archive", "node_modules", ".venv", "__pycache__", 
                "dist", "build", ".next", ".nuxt", "vendor", 
                ".pytest_cache", "coverage", ".idea", ".vscode"}

def write_tree(file_handle, dir_path: Path, prefix: str = '', is_last: bool = True, exclude_dirs: set = None):
    if exclude_dirs is None:
        exclude_dirs = set()
    
    # Konsolen-Feedback (Live-Update für den User)
    print(f"Scanne: {dir_path.resolve()}", flush=True)

    # Name des aktuellen Ordners in die Datei schreiben
    if prefix == '':
        file_handle.write(f"📁 {dir_path.name}/\n")
    else:
        connector = '└── ' if is_last else '├── '
        file_handle.write(f"{prefix}{connector}📁 {dir_path.name}/\n")
    
    # Direkt auf Festplatte wegschreiben!
    file_handle.flush() 
    
    try:
        entries = list(dir_path.iterdir())
    except PermissionError:
        file_handle.write(f"{prefix}{'    ' if is_last else '│   '}└── <Zugriff verweigert>\n")
        return

    # Filter out excluded dirs
    entries = [e for e in entries if not (e.is_dir() and e.name in exclude_dirs)]
    # Sort: Ordner zuerst, dann Dateien
    entries.sort(key=lambda x: (not x.is_dir(), x.name.lower()))
    
    for count, entry in enumerate(entries):
        is_last_entry = count == (len(entries) - 1)
        new_prefix = prefix + ('    ' if is_last else '│   ')
        
        if entry.is_dir():
            write_tree(file_handle, entry, new_prefix, is_last_entry, exclude_dirs)
        else:
            connector = '└── ' if is_last_entry else '├── '
            file_handle.write(f"{new_prefix}{connector}📄 {entry.name}\n")

def main():
    if len(sys.argv) < 3:
        print("Usage: python mini_packer.py <ziel_verzeichnis> <speicherort_verzeichnis>")
        sys.exit(1)
        
    target_dir = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])
    
    if not target_dir.is_dir():
        print(f"[FEHLER] Zielverzeichnis nicht gefunden: {target_dir}")
        sys.exit(1)
        
    if not output_dir.is_dir():
        print(f"[FEHLER] Speicherort nicht gefunden: {output_dir}")
        sys.exit(1)

    timestamp = time.strftime("%Y-%m-%d_%H-%M")
    target_name = target_dir.name if target_dir.name else str(target_dir).replace(':\\', '_Laufwerk')
    output_filename = output_dir / f"STRUKTUR_MAP_{target_name}_{timestamp}.md"
    
    print(f"[MINI-PACKER] Starte Live-Scan von '{target_dir}'...")
    print(f"[INFO] Datei wird in Echtzeit geschrieben: {output_filename}")
    
    with output_filename.open('w', encoding='utf-8') as f:
        f.write(f"# Struktur-Map: {target_dir}\n")
        f.write(f"> **Datum:** {timestamp}\n")
        f.write(f"> **Typ:** Nur Struktur (Live-Stream)\n\n")
        f.write("```text\n")
        
        # Starte den rekursiven Scan, der direkt in die Datei schreibt
        write_tree(f, target_dir, exclude_dirs=EXCLUDE_DIRS)
        
        f.write("```\n")
        
    print(f"\n[OK] Erfolgreich abgeschlossen! Datei: {output_filename}")

if __name__ == "__main__":
    main()
