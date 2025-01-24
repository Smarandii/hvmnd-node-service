# coding=utf-8
import os
import asyncio
from pyuac import main_requires_admin
from hvmnd_node_service_manager.service import HVMNDNodeService
from hvmnd_node_service_manager.utils import add_to_system_path


@main_requires_admin
def main():
    add_to_system_path("C:\\Program Files (x86)\\AnyDesk")

    hvmnd_node_service = HVMNDNodeService()
    asyncio.run(hvmnd_node_service.startup_node())
    asyncio.run(hvmnd_node_service.poll_node_status())


if __name__ == '__main__':
    main()
