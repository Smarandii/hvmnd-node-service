import os
import string
import random
import requests
import winreg as reg
from hvmnd_node_service_manager import logger


def generate_password(length=12):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


def send_telegram_message(token, chat_id, message, parse_mode=None):
    logger.info(f"Sending: {message} to {chat_id}. Parse_mode {parse_mode}")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message,
    }
    if parse_mode:
        data["parse_mode"] = parse_mode

    response = requests.post(url, params=data)
    return response.json()


def add_to_system_path(directory):
    key = reg.OpenKey(
        reg.HKEY_LOCAL_MACHINE,
        r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment',
        0,
        reg.KEY_ALL_ACCESS
    )

    try:
        current_path = reg.QueryValueEx(key, 'Path')[0]

        if str(directory) not in current_path:
            new_path = current_path + ";" + str(directory)
            reg.SetValueEx(key, 'Path', 0, reg.REG_EXPAND_SZ, new_path)
            print(f"Added {directory} to system PATH.")
        else:
            print(f"{directory} is already in the system PATH.")
    finally:
        reg.CloseKey(key)


def update_hosts_file(host: str, ip: str, hosts_path: str = r"C:\Windows\System32\drivers\etc\hosts"):
    """
    Checks if the specified host is already mapped in the hosts file.
    If not, appends an entry mapping the host to the given IP.
    """
    if not os.path.exists(hosts_path):
        logger.error(f"Hosts file not found at {hosts_path}")
        return

    try:
        with open(hosts_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        logger.error(f"Unable to open hosts file for reading: {e}")
        return

    entry_exists = False
    for line in lines:
        # Remove comments and ignore blank lines
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        # Split the line into tokens (IP and hostnames)
        tokens = stripped.split()
        if len(tokens) < 2:
            continue
        # Check if the host is already present in the list of hostnames
        if host in tokens[1:]:
            entry_exists = True
            break

    if not entry_exists:
        new_entry = f"\n{ip}\t{host}\n"
        try:
            with open(hosts_path, "a", encoding="utf-8") as f:
                f.write(new_entry)
            logger.info(f"Added hosts file entry: {new_entry.strip()}")
        except Exception as e:
            logger.error(f"Failed to write to hosts file: {e}")
    else:
        logger.info(f"Hosts file already contains an entry for {host}")


if __name__ == "__main__":
    add_to_system_path("C:\\Program Files (x86)\\AnyDesk\\")
    update_hosts_file("prod.hvmnd-api.freemyip.com", "95.217.142.240")

