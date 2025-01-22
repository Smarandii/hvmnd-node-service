@echo off
setlocal

echo Pulling latest code...
git pull origin master || echo Git pull failed! && exit /b 1

echo Activating virtual environment and updating service...
powershell -ExecutionPolicy Bypass -Command ". .\venv\Scripts\activate; python render_node_setup.py" || echo Service setup failed! && exit /b 1

echo Script completed successfully.
endlocal
exit /b 0
