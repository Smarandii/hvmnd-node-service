# coding=utf-8
import time
import socket

import requests
import ngrok
from render_node_manager.app import app
from render_node_manager.db_operations import save_or_update_ngrok_url
from pyuac import main_requires_admin


def send_telegram_message(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message,
    }
    response = requests.post(url, params=data)
    return response.json()


@main_requires_admin
def main():
    listener = ngrok.connect(5000, authtoken_from_env=True)
    print(f"Ingress established at {listener.url()}")
    save_or_update_ngrok_url(listener.url())
    app.run(port=5000, debug=False)


if __name__ == '__main__':
    token = "6524183208:AAHXOGhNtuQ1mHis-3J9_tsd01ZI0CTIX60"
    chat_id = "231584958"
    send_telegram_message(token=token, chat_id=chat_id, message=str(f"{socket.gethostname()} Node available"))
    while True:
        try:
            main()
        except Exception as e:
            send_telegram_message(token=token, chat_id=chat_id, message=str(e))
            time.sleep(60)

