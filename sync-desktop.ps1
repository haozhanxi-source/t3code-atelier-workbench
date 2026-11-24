# One-click sync of Atelier Workbench theme + 4K wallpaper to Windows T3 Code Desktop.
# Pass -InstallFonts to also install official open-source Noto Serif CJK SC (Regular + Medium) per-user.
param(
    [switch]$InstallFonts
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$T3Home = if ($env:T3CODE_HOME) { $env:T3CODE_HOME } else { Join-Path $HOME ".t3" }
$TargetDir = Join-Path $T3Home "userdata\themes"
New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null
Copy-Item -Force (Join-Path $ScriptDir "atelier-workbench.json") (Join-Path $TargetDir "atelier-workbench.json")
Copy-Item -Force (Join-Path $ScriptDir "atelier-workbench.webp") (Join-Path $TargetDir "atelier-workbench.webp")
$StalePng = Join-Path $TargetDir "atelier-workbench.png"
if (Test-Path $StalePng) { Remove-Item -Force $StalePng }
Write-Host "Installed Atelier Workbench theme to $TargetDir"

if ($InstallFonts) {
    $FontDest = Join-Path $env:LOCALAPPDATA "Microsoft\Windows\Fonts"
    New-Item -ItemType Directory -Force -Path $FontDest | Out-Null
    $RegPath = "HKCU:\Software\Microsoft\Windows NT\CurrentVersion\Fonts"
    $BaseUrl = "https://raw.githubusercontent.com/notofonts/noto-cjk/main/Serif/OTF/SimplifiedChinese"
    $Fonts = @(
        @{ File = "NotoSerifCJKsc-Regular.otf"; RegName = "Noto Serif CJK SC Regular (OpenType)"; Sha256 = "2a2eae2628df83556c54018c41e20fa532c1b862c5256ae8b3f23feb918d12ca" },
        @{ File = "NotoSerifCJKsc-Medium.otf";  RegName = "Noto Serif CJK SC Medium (OpenType)";  Sha256 = "19322be2ecf5dd2abd546db7a86cc83c286026cbd28593583bfcfd721e48c9fe" }
    )

    Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public static class AtelierFontApi {
    [DllImport("gdi32.dll", CharSet = CharSet.Unicode)]
    public static extern int AddFontResourceW(string lpFileName);
    [DllImport("user32.dll", SetLastError = true, CharSet = CharSet.Unicode)]
    public static extern IntPtr SendMessageTimeoutW(IntPtr hWnd, uint Msg, IntPtr wParam, IntPtr lParam, uint fuFlags, uint uTimeout, out IntPtr lpdwResult);
}
"@

    $TmpDir = Join-Path $env:TEMP "atelier-fonts-download"
    New-Item -ItemType Directory -Force -Path $TmpDir | Out-Null
    try {
        foreach ($item in $Fonts) {
            $tmpFile = Join-Path $TmpDir $item.File
            $url = "$BaseUrl/$($item.File)"
            Write-Host "Downloading $($item.File)..."
            Invoke-WebRequest -UseBasicParsing -Uri $url -OutFile $tmpFile
            $actual = (Get-FileHash -Algorithm SHA256 -Path $tmpFile).Hash.ToLowerInvariant()
            if ($actual -ne $item.Sha256) {
                throw "SHA-256 mismatch for $($item.File): expected $($item.Sha256), got $actual"
            }
            $destPath = Join-Path $FontDest $item.File
            Copy-Item -Force $tmpFile $destPath
            Set-ItemProperty -Path $RegPath -Name $item.RegName -Value $destPath
            [void][AtelierFontApi]::AddFontResourceW($destPath)
            Write-Host "Installed $($item.File) to $destPath"
        }
        $res = [IntPtr]::Zero
        [void][AtelierFontApi]::SendMessageTimeoutW([IntPtr]0xFFFF, 0x001D, [IntPtr]::Zero, [IntPtr]::Zero, 2, 1000, [ref]$res)
        Write-Host "Restart T3 Code (or your browser) to pick up newly installed fonts."
    } finally {
        Remove-Item -Recurse -Force -ErrorAction SilentlyContinue $TmpDir
    }
}

Write-Host "In T3 Code Desktop: Settings -> Appearance -> Theme -> Atelier Workbench · 砚纸精工 (System auto day/night)"

