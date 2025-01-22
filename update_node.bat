@echo off
setlocal

echo Updating service... > update_node.log
git pull origin master || echo Git pull failed! && exit /b 1

echo Activating virtual environment and updating service... > update_node.log
powershell -ExecutionPolicy Bypass -Command ". .\venv\Scripts\activate; python render_node_setup.py" || echo Service setup failed! > update_node.log && exit /b 1

echo Script completed successfully. > update_node.log
endlocal
exit /b 0
