# coding=utf-8
import os
import asyncio
from pyuac import main_requires_admin
from render_node_manager.db_operations import DBOperations
from render_node_manager.utils import add_to_system_path


@main_requires_admin
def main():
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    NSSM_ZIP_URL = 'https://nssm.cc/release/nssm-2.24.zip'
    NSSM_ZIP_PATH = os.path.join(ROOT_DIR, 'nssm-2.24.zip')
    print("Downloading NSSM...")
    if not os.path.exists(NSSM_ZIP_PATH):
        urllib.request.urlretrieve(NSSM_ZIP_URL, NSSM_ZIP_PATH)
    else:
        print(f"NSSM already downloaded {NSSM_ZIP_PATH}")

    NSSM_EXE_PATH = os.path.join(ROOT_DIR, 'nssm-2.24', 'win64', 'nssm.exe')
    NSSM_EXE_FOLDER_PATH = os.path.join(ROOT_DIR, 'nssm-2.24', 'win64')
    print(f"NSSM_EXE_PATH: {NSSM_EXE_PATH}")

    # Step 5: Unzip NSSM
    print("Unzipping NSSM...")
    if not os.path.exists(NSSM_EXE_PATH):
        with zipfile.ZipFile(NSSM_ZIP_PATH, 'r') as zip_ref:
            zip_ref.extractall(NSSM_EXTRACT_DIR)
    else:
        print(f"NSSM already unzipped and ready to use {NSSM_EXE_PATH}")
    add_to_system_path("C:\\Program Files (x86)\\AnyDesk")
    add_to_system_path(str(NSSM_EXE_FOLDER_PATH))

    dbo = DBOperations()

    asyncio.run(dbo.startup_node())
    asyncio.run(dbo.poll_node_status())


if __name__ == '__main__':
    main()
