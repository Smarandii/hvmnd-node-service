# coding=utf-8
import socket
import asyncio
import time

from pyuac import main_requires_admin
from hvmnd_node_service_manager.service import HVMNDNodeService
from hvmnd_node_service_manager.utils import add_to_system_path, update_hosts_file, send_telegram_message
from hvmnd_node_service_manager.config import ALERT_BOT_TOKEN, ADMIN_CHAT_ID


@main_requires_admin
def main():
    try:
        add_to_system_path("C:\\Program Files (x86)\\AnyDesk")
        update_hosts_file("prod.hvmnd-api.freemyip.com", "95.217.142.240")

        hvmnd_node_service = HVMNDNodeService()
        hvmnd_node_service.startup_node()
        asyncio.run(hvmnd_node_service.poll_node_status())
    except Exception as e:
        send_telegram_message(
            token=ALERT_BOT_TOKEN,
            chat_id=ADMIN_CHAT_ID,
            message=f"Critical Error Occurred on {socket.gethostname()} - {e}"
        )
        time.sleep(60)


if __name__ == '__main__':
    main()
