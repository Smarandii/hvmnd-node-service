@echo off
setlocal

REM Define download URLs
set "GIT_URL=https://github.com/git-for-windows/git/releases/download/v2.45.2.windows.1/Git-2.45.2-64-bit.exe"
set "PYTHON_URL=https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe"

REM Define file paths
set "GIT_INSTALLER=%temp%\Git-2.45.2-64-bit.exe"
set "PYTHON_INSTALLER=%temp%\python-3.12.0-amd64.exe"

REM Download Git installer
echo Downloading Git installer...
powershell -Command "Invoke-WebRequest -Uri %GIT_URL% -OutFile %GIT_INSTALLER%"
if %ERRORLEVEL% neq 0 (
    echo Failed to download Git installer.
    exit /b 1
)

REM Download Python installer
echo Downloading Python installer...
powershell -Command "Invoke-WebRequest -Uri %PYTHON_URL% -OutFile %PYTHON_INSTALLER%"
if %ERRORLEVEL% neq 0 (
    echo Failed to download Python installer.
    exit /b 1
)

REM Install Git silently
echo Installing Git...
%GIT_INSTALLER% /VERYSILENT /NORESTART
if %ERRORLEVEL% neq 0 (
    echo Failed to install Git.
    exit /b 1
)

REM Install Python silently
echo Installing Python...
%PYTHON_INSTALLER% /quiet InstallAllUsers=1 PrependPath=1
if %ERRORLEVEL% neq 0 (
    echo Failed to install Python.
    exit /b 1
)

echo Script completed successfully.
endlocal
exit /b 0
