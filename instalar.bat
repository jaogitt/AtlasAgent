@echo off
cd /d "%~dp0"
where py >nul 2>&1
if %errorlevel%==0 (set "PY=py") else (set "PY=python")
%PY% -m venv .venv
if errorlevel 1 (echo Falha ao criar ambiente Python. & pause & exit /b 1)
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 (echo Falha ao instalar dependencias. & pause & exit /b 1)
if not exist .env copy .env.example .env >nul
echo.
echo Instalado! Edite .env com sua NVIDIA_API_KEY.
echo Depois execute iniciar.bat ou .\atlas.ps1
pause
