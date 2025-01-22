@echo off
setlocal

:: Define log file
set LOGFILE=update_node.log

echo Running under user: %USERNAME% >> "%LOGFILE%"
whoami >> "%LOGFILE%"

:: Start logging
echo Updating service... > "%LOGFILE%"

echo Stopping render-node-service... >> "%LOGFILE%"

:: Try stopping the service
sc stop render-node-service >> "%LOGFILE%" 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo "Service stop command failed, attempting taskkill..." >> "%LOGFILE%"
    for /f "tokens=2 delims= " %%i in ('tasklist /fi "imagename eq python.exe" /fi "services eq render-node-service"') do taskkill /pid %%i /f >> "%LOGFILE%" 2>&1
)

echo "TEST..." >> "%LOGFILE%"

if %ERRORLEVEL% NEQ 0 (
    echo Failed to stop service! >> "%LOGFILE%"
)

echo Service stopped successfully. >> "%LOGFILE%"

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