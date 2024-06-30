import os
import subprocess
import zipfile
import urllib.request
from time import sleep

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
if not os.path.exists(NSSM_ZIP_PATH):
    urllib.request.urlretrieve(NSSM_ZIP_URL, NSSM_ZIP_PATH)
else:
    print(f"NSSM already downloaded {NSSM_ZIP_PATH}")

NSSM_EXE_PATH = os.path.join(ROOT_DIR, 'nssm-2.24', 'win64', 'nssm.exe')  # Adjust based on NSSM's zip structure

# Step 5: Unzip NSSM
print("Unzipping NSSM...")
if not os.path.exists(NSSM_EXE_PATH):
    with zipfile.ZipFile(NSSM_ZIP_PATH, 'r') as zip_ref:
        zip_ref.extractall(NSSM_EXTRACT_DIR)
else:
    print(f"NSSM already unzipped and ready to use {NSSM_EXE_PATH}")


# Step 6: Setup NSSM service
print("Setting up NSSM service...")

try:
    subprocess.check_call([NSSM_EXE_PATH, 'remove', 'render-node-service', 'confirm'])
    print("waiting for service to be removed")
    sleep(15)
except Exception as e:
    print("service is not installed...\nproceeding to installation...")

try:
    subprocess.check_call([NSSM_EXE_PATH, 'install', 'render-node-service', PYTHON_EXE, MAIN_PY_PATH])
except Exception as e:
    print("render-node-service already installed")

try:
    subprocess.check_call([NSSM_EXE_PATH, 'start', 'render-node-service'])
except Exception as e:
    print("render-node-service already started")


print("Setup completed successfully.")
