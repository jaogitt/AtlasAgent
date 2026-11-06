$project = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not (Test-Path "$project\.venv\Scripts\python.exe")) { Write-Error 'Execute instalar.bat primeiro.'; exit 1 }
& "$project\.venv\Scripts\python.exe" "$project\main.py"
