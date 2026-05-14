param(
    [switch]$DryRun,
    [switch]$NoMirror
)

$Source = "E:\_____1111____Projekte-Programmierung\Antigravity"
$Target = "G:\Meine Ablage\_Projekte-Programmierung\Antigravity\"

# Exclusions based on RB-Protokoll and Virtual Environments
$ExcludeDirs = @(".git", "node_modules", "*venv*", ".*venv*", "env", ".*env*", "virtualenv", ".virtualenv", "__pycache__", ".rb_dumps", ".idea", ".vscode", "_archive", "_rb_dumps")
$ExcludeFiles = @(".env", "*.pyc", "*.log", "*.tmp", "__System OS Deployment")

# RoboCopy Options: /E (recursive), /Z (restartable), /R (retries), /W (wait), /V (verbose), /MT (multithreaded), /TBD (top level directory), /NP (no progress)
$RoboOptions = @("/E", "/Z", "/R:3", "/W:5", "/V", "/MT:16", "/TBD", "/NP")

if (-not $NoMirror) {
    $RoboOptions += "/MIR"
}

if ($DryRun) {
    $RoboOptions += "/L"
    Write-Host ">>> DRY RUN: Keine Dateien werden kopiert! <<<" -ForegroundColor Yellow
}

$LogDir = Join-Path $Source "_rb-Protokoll\logs"
if (-not (Test-Path -Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

$Timestamp = Get-Date -Format 'yyyy-MM-dd_HH-mm'
$LogFile = "sync_$Timestamp.log"
$LogPath = Join-Path $LogDir $LogFile

Write-Host "Syncing Antigravity to Cloud..." -ForegroundColor Cyan
Write-Host "Source: $Source"
Write-Host "Target: $Target"

# Check target availability
if (-not (Test-Path $Target)) {
    Write-Error "Cloud-Ziel $Target ist nicht verfügbar! Stelle sicher, dass Laufwerk G: (Google Drive) eingebunden ist."
    exit 1
}

# Invoke Robocopy with fully quoted paths
# Note: Robocopy is sensitive to trailing backslashes inside quotes, so we ensure they are clean.
$SourcePath = $Source.TrimEnd("\")
$TargetPath = $Target.TrimEnd("\")

$cmdArgs = @("$SourcePath", "$TargetPath")
$cmdArgs += $RoboOptions
$cmdArgs += "/XD"
$cmdArgs += $ExcludeDirs
$cmdArgs += "/XF"
$cmdArgs += $ExcludeFiles
$cmdArgs += "/LOG:$LogPath"

robocopy @cmdArgs

$ExitCode = $LASTEXITCODE

# Exit Codes: 0-7 are success/minor warnings, 8+ are errors
if ($ExitCode -le 7) {
    Write-Host "Sync erfolgreich (Exit Code: $ExitCode)" -ForegroundColor Green
    Write-Host "Log: $LogPath"
} else {
    Write-Host "Sync hatte Fehler (Exit Code: $ExitCode). Prüfe das Log: $LogPath" -ForegroundColor Red
}
