# coding=utf-8
import asyncio
from pyuac import main_requires_admin
from hvmnd_node_service_manager.service import HVMNDNodeService
from hvmnd_node_service_manager.utils import add_to_system_path, update_hosts_file


@main_requires_admin
def main():
    add_to_system_path("C:\\Program Files (x86)\\AnyDesk")
    update_hosts_file("prod.hvmnd-api.freemyip.com", "95.217.142.240")

    hvmnd_node_service = HVMNDNodeService()
    hvmnd_node_service.startup_node()
    asyncio.run(hvmnd_node_service.poll_node_status())


if __name__ == '__main__':
    main()
