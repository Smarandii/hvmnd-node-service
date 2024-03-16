import socket
import string
import random
import psutil
import GPUtil

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
