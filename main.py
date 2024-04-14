# coding=utf-8
import time
from render_node_manager.db_operations import DBOperations
from pyuac import main_requires_admin
from render_node_manager.config import token, chat_id
from render_node_manager.utils import send_telegram_message


@main_requires_admin
def main():
    dbo = DBOperations()
    dbo.startup_node()
    dbo.poll_node_status()


if __name__ == '__main__':
    while True:
        try:
            main()
        except Exception as e:
            send_telegram_message(token=token, chat_id=chat_id, message=str(e))
            time.sleep(60)

