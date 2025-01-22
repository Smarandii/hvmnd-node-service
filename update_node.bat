@echo off
setlocal

:: Define log file
set LOGFILE=update_node.log

nssm stop render-node-service >> update_node.log 2>&1 || echo Failed to stop service! >> "%LOGFILE%" && exit /b 1

:: Start logging
echo Updating service... > "%LOGFILE%"

:: Pull latest code
echo Pulling latest code... >> "%LOGFILE%"
git remote add origin-update "https://Smarandii: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@github.com/Smarandii/hvmnd-node-service.git" >> "%LOGFILE%" 2>&1
git pull origin-update master >> "%LOGFILE%" 2>&1

if %ERRORLEVEL% NEQ 0 (
    echo Git pull failed! >> "%LOGFILE%"
    exit /b 1
)

:: Run Python script directly without activating the environment
echo Running service setup... >> "%LOGFILE%"
.\venv\Scripts\python.exe render_node_setup.py >> "%LOGFILE%" 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Service setup failed! >> "%LOGFILE%"
    exit /b 1
)

:: Finish logging
echo Script completed successfully. >> "%LOGFILE%"
endlocal
exit /b 0