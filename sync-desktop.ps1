# One-click sync of Atelier Workbench theme + 4K wallpaper to Windows T3 Code Desktop
$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$T3Home = if ($env:T3CODE_HOME) { $env:T3CODE_HOME } else { Join-Path $HOME ".t3" }
$TargetDir = Join-Path $T3Home "userdata\themes"
New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null
Copy-Item -Force (Join-Path $ScriptDir "atelier-workbench.json") (Join-Path $TargetDir "atelier-workbench.json")
Copy-Item -Force (Join-Path $ScriptDir "atelier-workbench.webp") (Join-Path $TargetDir "atelier-workbench.webp")
Write-Host "Installed Atelier Workbench theme to $TargetDir"
Write-Host "In T3 Code Desktop: Settings -> Appearance -> Theme -> Atelier Workbench · 砚纸精工 (System auto day/night)"
