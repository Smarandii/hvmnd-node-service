import os
import subprocess
import zipfile
import urllib.request

# Define paths
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
VENV_DIR = os.path.join(ROOT_DIR, 'venv')
PYTHON_EXE = os.path.join(VENV_DIR, 'Scripts', 'python.exe')
REQUIREMENTS_PATH = os.path.join(ROOT_DIR, 'requirements.txt')
MAIN_PY_PATH = os.path.join(ROOT_DIR, 'main.py')
NSSM_ZIP_URL = 'https://nssm.cc/release/nssm-2.24.zip'
NSSM_ZIP_PATH = os.path.join(ROOT_DIR, 'nssm-2.24.zip')
NSSM_EXTRACT_DIR = ROOT_DIR

# Step 1: Create virtual environment
print("Creating virtual environment...")
try:
    subprocess.check_call(['py', '-m', 'venv', 'venv'])
except subprocess.CalledProcessError:
    print("Virtual environment already exists")

# Step 2 is handled by invoking pip through the created virtual environment's Python executable

# Step 3: Install requirements.txt
print("Installing dependencies from requirements.txt...")
subprocess.check_call([PYTHON_EXE, '-m', 'pip', 'install', '-r', REQUIREMENTS_PATH])

# Step 4: Download NSSM
print("Downloading NSSM...")
urllib.request.urlretrieve(NSSM_ZIP_URL, NSSM_ZIP_PATH)

# Step 5: Unzip NSSM
print("Unzipping NSSM...")
with zipfile.ZipFile(NSSM_ZIP_PATH, 'r') as zip_ref:
    zip_ref.extractall(NSSM_EXTRACT_DIR)

# The extracted directory name will depend on the NSSM version and structure of the zip file
# Adjust this path as necessary based on the actual contents of the NSSM zip file
NSSM_EXE_PATH = os.path.join(ROOT_DIR, 'nssm-2.24', 'win64', 'nssm.exe')  # Adjust based on NSSM's zip structure

# Step 6: Setup NSSM service
print("Setting up NSSM service...")
subprocess.check_call([NSSM_EXE_PATH, 'remove', 'render-node-service'])
subprocess.check_call([NSSM_EXE_PATH, 'install', 'render-node-service', PYTHON_EXE, MAIN_PY_PATH])
subprocess.check_call([NSSM_EXE_PATH, 'start', 'render-node-service'])

print("Setup completed successfully.")
