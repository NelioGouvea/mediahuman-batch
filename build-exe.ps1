$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

python -m venv .venv-build
.venv-build\Scripts\python -m pip install --upgrade pip
.venv-build\Scripts\python -m pip install -r requirements.txt "pyinstaller>=6.22"
.venv-build\Scripts\python -m PyInstaller --noconfirm --onefile --windowed `
    --name MediaHumanBatch --paths . --specpath build --distpath dist app\__main__.py

Write-Host "Executável gerado: dist\MediaHumanBatch.exe"
