@echo off
SET projectDir="C:\Program Files (x86)\render_hive_farm_bot_node_service"
SET venvDir="%projectDir%\venv"

cd %projectDir%

IF NOT EXIST %venvDir% (
    python -m venv venv
    echo Virtual environment created.
)

call "%venvDir%\Scripts\activate"

IF NOT EXIST "%venvDir%\Scripts\pip.exe" (
    echo Installing pip...
    python -m ensurepip
)

echo Installing dependencies...
pip install -r requirements.txt

echo Starting application...
pythonw main.py > "%projectDir%\app_output.log" 2>&1


