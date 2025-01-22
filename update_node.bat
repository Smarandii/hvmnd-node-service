@echo off
setlocal

:: Define log file
set LOGFILE=update_node.log

:: Start logging
echo Updating service... > "%LOGFILE%"

:: Pull latest code
echo Pulling latest code... >> "%LOGFILE%"
git pull origin master >> "%LOGFILE%" 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Git pull failed! >> "%LOGFILE%"
    exit /b 1
)

:: Activate virtual environment and update service
echo Activating virtual environment and updating service... >> "%LOGFILE%"
powershell -ExecutionPolicy Bypass -Command ". .\venv\Scripts\activate; python render_node_setup.py" >> "%LOGFILE%" 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Service setup failed! >> "%LOGFILE%"
    exit /b 1
)

:: Finish logging
echo Script completed successfully. >> "%LOGFILE%"
endlocal
exit /b 0
