$ErrorActionPreference = 'Stop'

$Repository = 'jaogitt/AtlasAgent'
$Branch = 'main'
$InstallPath = Join-Path $env:LOCALAPPDATA 'Programs\AtlasAgent'

if ($Repository -match 'OWNER|REPOSITORY' -or $Repository -notmatch '^[^/]+/[^/]+$') {
    throw 'O repositório configurado no install.ps1 é inválido.'
}

if (Test-Path -LiteralPath $InstallPath) {
    throw "O destino já existe: $InstallPath. Remova ou mova a instalação anterior antes de instalar novamente."
}

$Python = Get-Command py -ErrorAction SilentlyContinue
$PythonArgs = @()
if ($Python) {
    $PythonArgs = @('-3')
} else {
    $Python = Get-Command python -ErrorAction SilentlyContinue
}
if (-not $Python) {
    throw 'Python 3.11+ não foi encontrado. Instale Python e execute este comando novamente.'
}

$TempPath = Join-Path $env:TEMP ("atlas-agent-install-" + [guid]::NewGuid().ToString('N'))
$ArchivePath = Join-Path $TempPath 'source.zip'

try {
    New-Item -ItemType Directory -Path $TempPath | Out-Null
    $ArchiveUri = "https://github.com/$Repository/archive/refs/heads/$Branch.zip"
    Invoke-WebRequest -Uri $ArchiveUri -OutFile $ArchivePath -UseBasicParsing
    Expand-Archive -LiteralPath $ArchivePath -DestinationPath $TempPath

    $SourcePath = Get-ChildItem -LiteralPath $TempPath -Directory | Select-Object -First 1 -ExpandProperty FullName
    if (-not $SourcePath -or -not (Test-Path -LiteralPath (Join-Path $SourcePath 'requirements.txt'))) {
        throw 'O ZIP baixado não contém o código esperado do ATLAS AGENT.'
    }

    New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null
    Get-ChildItem -LiteralPath $SourcePath -Force | ForEach-Object {
        Copy-Item -LiteralPath $_.FullName -Destination $InstallPath -Recurse -Force
    }

    $VenvPython = Join-Path $InstallPath '.venv\Scripts\python.exe'
    & $Python.Source @PythonArgs -m venv (Join-Path $InstallPath '.venv')
    if ($LASTEXITCODE -ne 0) { throw 'Não foi possível criar o ambiente Python.' }

    & $VenvPython -m pip install -r (Join-Path $InstallPath 'requirements.txt')
    if ($LASTEXITCODE -ne 0) { throw 'Não foi possível instalar as dependências Python.' }

    $EnvPath = Join-Path $InstallPath '.env'
    Copy-Item -LiteralPath (Join-Path $InstallPath '.env.example') -Destination $EnvPath

    Write-Host ''
    Write-Host "ATLAS AGENT instalado em: $InstallPath" -ForegroundColor Green
    Write-Host "Edite $EnvPath e informe sua NVIDIA_API_KEY."
    Write-Host "Para abrir no workspace atual: & '$InstallPath\atlas.ps1'"
} finally {
    if (Test-Path -LiteralPath $TempPath) {
        Remove-Item -LiteralPath $TempPath -Recurse -Force
    }
}
