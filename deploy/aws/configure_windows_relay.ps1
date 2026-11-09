param(
    [ValidateSet('Enable', 'Disable', 'Status')]
    [string]$Action = 'Status'
)
$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$python = Join-Path $projectRoot '.venv\Scripts\python.exe'
$pythonWindowless = Join-Path $projectRoot '.venv\Scripts\pythonw.exe'
$watcher = Join-Path $PSScriptRoot 'watch_github_main.py'
$runtimeDirectory = Join-Path $projectRoot '.runtime\auto-deploy'
$enabledFile = Join-Path $runtimeDirectory 'windows-relay.enabled'
$stateFile = Join-Path $runtimeDirectory 'windows-relay.json'
$startupDirectory = [Environment]::GetFolderPath('Startup')
$shortcutPath = Join-Path $startupDirectory 'MoveInMate P-047 AutoDeploy.lnk'

function Get-RelayProcesses {
    @(Get-CimInstance Win32_Process -Filter "Name='pythonw.exe'" | Where-Object {
        $_.CommandLine -and $_.CommandLine.Contains($watcher) -and $_.CommandLine.Contains('--loop')
    })
}

function Confirm-OwnShortcut {
    if (Test-Path -LiteralPath $shortcutPath) {
        $shell = New-Object -ComObject WScript.Shell
        $shortcut = $shell.CreateShortcut($shortcutPath)
        if ($shortcut.TargetPath -ne $pythonWindowless -or -not $shortcut.Arguments.Contains($watcher)) {
            throw 'Startup shortcut belongs to another installation; refusing to replace or delete it.'
        }
    }
}

if ($Action -eq 'Enable') {
    foreach ($path in @($python, $pythonWindowless, $watcher)) {
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "Missing required file: $path" }
    }
    # Use the current user's Git Credential Manager. Nothing is sent to another user or saved on EC2.
    & $python $watcher --check
    if ($LASTEXITCODE -ne 0) { throw 'GitHub read-access preflight failed; relay was not enabled.' }
    Confirm-OwnShortcut
    New-Item -ItemType Directory -Path $runtimeDirectory -Force | Out-Null
    New-Item -ItemType Directory -Path $startupDirectory -Force | Out-Null
    Set-Content -LiteralPath $enabledFile -Value 'enabled' -Encoding Ascii
    $shell = New-Object -ComObject WScript.Shell
    $shortcut = $shell.CreateShortcut($shortcutPath)
    $shortcut.TargetPath = $pythonWindowless
    $shortcut.Arguments = '"' + $watcher + '" --loop'
    $shortcut.WorkingDirectory = $projectRoot
    $shortcut.Description = 'Deploy GitHub main to MoveInMate while this Windows user is signed in.'
    $shortcut.WindowStyle = 7
    $shortcut.Save()
    if ((Get-RelayProcesses).Count -eq 0) {
        Start-Process -FilePath $pythonWindowless -ArgumentList $shortcut.Arguments -WorkingDirectory $projectRoot -WindowStyle Hidden
    }
} elseif ($Action -eq 'Disable') {
    Confirm-OwnShortcut
    if (Test-Path -LiteralPath $shortcutPath) { Remove-Item -LiteralPath $shortcutPath }
    if (Test-Path -LiteralPath $enabledFile) { Remove-Item -LiteralPath $enabledFile }
}

$state = $null
if (Test-Path -LiteralPath $stateFile) { $state = Get-Content -LiteralPath $stateFile -Raw | ConvertFrom-Json }
[pscustomobject]@{
    enabled = (Test-Path -LiteralPath $enabledFile)
    starts_at_windows_signin = (Test-Path -LiteralPath $shortcutPath)
    process_ids = @((Get-RelayProcesses) | ForEach-Object { $_.ProcessId })
    state = $state
} | ConvertTo-Json -Depth 5
