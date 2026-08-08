# Open ADS (if not running) and auto-open the Python Console
# Usage: powershell -ExecutionPolicy Bypass -File ADS\ads_tools\open_ads_console.ps1
$adsExe = "D:\Program Files\Keysight\ADS2025_Update2\bin\ads.exe"
if ($env:HPEESOF_DIR) { $adsExe = "$env:HPEESOF_DIR\bin\ads.exe" }

Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public class FGWin {
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int n);
}
"@

# 1) Make sure ADS is running
$proc = Get-Process -Name hpeesofde -ErrorAction SilentlyContinue |
        Where-Object { $_.MainWindowHandle -ne 0 } | Select-Object -First 1
if (-not $proc) {
    Write-Host "[1/3] Starting ADS..."
    Start-Process $adsExe
    for ($i = 0; $i -lt 30; $i++) {
        Start-Sleep -Seconds 1
        $proc = Get-Process -Name hpeesofde -ErrorAction SilentlyContinue |
                Where-Object { $_.MainWindowHandle -ne 0 } | Select-Object -First 1
        if ($proc) { break }
    }
}
if (-not $proc) { Write-Host "ADS not ready"; exit 1 }
Write-Host "[2/3] ADS running (PID $($proc.Id))"

# 2) Bring ADS window to foreground
[FGWin]::ShowWindow($proc.MainWindowHandle, 9) | Out-Null   # 9 = SW_RESTORE
[FGWin]::SetForegroundWindow($proc.MainWindowHandle) | Out-Null
Start-Sleep -Milliseconds 800

# 3) Send Python Console shortcut: Ctrl+Shift+P
$ws = New-Object -ComObject WScript.Shell
$ws.SendKeys("^+p")
Write-Host "[3/3] Sent Ctrl+Shift+P -> Python Console should open"
