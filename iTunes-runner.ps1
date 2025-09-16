$pythonScriptPath = "itunes_updater.py"

$itunesPath = "C:\Program Files\iTunes\iTunes.exe"

Function Send-CtrlC {
    param(
        [Parameter(Mandatory=$true)]
        [int]$ProcessId
    )

    $sig = "[System.Runtime.InteropServices.DllImport(`"kernel32.dll`")][void] extern static BOOL GenerateConsoleCtrlEvent(DWORD dwCtrlEvent, DWORD dwProcessGroupId);"
    Add-Type -TypeDefinition $sig -Name "Win32API" -Namespace "W32"
    
    $result = [W32.Win32API]::GenerateConsoleCtrlEvent(0, $ProcessId)
    if (-not $result) {
        throw "Failed to send Ctrl+C signal."
    }
}

Write-Host "Starting iTunes monitor and iTunes..."

$pythonProcess = Start-Process -FilePath "python.exe" -ArgumentList $pythonScriptPath -PassThru -NoNewWindow

$itunesProcess = Start-Process -FilePath $itunesPath -PassThru -NoNewWindow

Start-Sleep -Seconds 5

Write-Host "iTunes Monitor is now running. Close this window to shut down all processes."
Write-Host "To shut down gracefully, use Ctrl+C in this window."
Write-Host ""
Write-Host "--------------------"
Write-Host "Python Script Output:"

try {
    while ($true) {
        Start-Sleep -Seconds 1
    }
}
finally {
    Write-Host "Shutting down..."

    if (-not $pythonProcess.HasExited) {
        Write-Host "Sending Ctrl+C signal to Python script..."
        Send-CtrlC -ProcessId $pythonProcess.Id
        Start-Sleep -Seconds 3
    }

    if (-not $itunesProcess.HasExited) {
        Write-Host "Terminating iTunes..."
        Stop-Process -Id $itunesProcess.Id -Force
    }

    Write-Host "All processes have been closed."
    Start-Sleep -Seconds 2
}