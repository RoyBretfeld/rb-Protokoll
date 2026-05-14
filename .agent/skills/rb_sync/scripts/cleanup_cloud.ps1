param(
    [switch]$WhatIf
)

$Target = "G:\Meine Ablage\_Projekte-Programmierung\Antigravity\"

# Folders to delete (virtual environments and large/temp caches)
$ToCleanup = @("*venv*", ".*venv*", "node_modules", ".rb_dumps", "__pycache__", ".idea", ".vscode")

Write-Host "Reinigungs-Lauf in der Cloud wird vorbereitet..." -ForegroundColor Cyan
Write-Host "Ziel: $Target"

if (-not (Test-Path $Target)) {
    Write-Error "Cloud-Ziel nicht verfügbar!"
    exit 1
}

foreach ($Pattern in $ToCleanup) {
    Write-Host "Suche nach: $Pattern" -ForegroundColor Yellow
    $Found = Get-ChildItem -Path $Target -Filter $Pattern -Recurse -Directory -ErrorAction SilentlyContinue
    
    if ($Found) {
        foreach ($Folder in $Found) {
            Write-Host "Lösche: $($Folder.FullName)" -ForegroundColor Red
            if ($WhatIf) {
                Write-Host "(Simuliert: Datei wird nicht gelöscht)" -ForegroundColor Gray
            } else {
                try {
                    # Remove folder forcefully
                    Remove-Item -Path $Folder.FullName -Recurse -Force -ErrorAction Stop
                } catch {
                    Write-Host "Fehler beim Löschen von $($Folder.FullName): $($_.Exception.Message)" -ForegroundColor DarkGray
                }
            }
        }
    } else {
        Write-Host "Nichts gefunden für $Pattern." -ForegroundColor Green
    }
}

Write-Host "Reinigung abgeschlossen." -ForegroundColor Cyan
