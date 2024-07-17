# coding=utf-8
import asyncio
from pyuac import main_requires_admin
from render_node_manager.db_operations import DBOperations
from render_node_manager.utils import add_to_system_path


@main_requires_admin
def main():
    add_to_system_path("E:\\ProgramFiles(x86)\\AnyDesk")
    dbo = DBOperations()

    asyncio.run(dbo.startup_node())
    asyncio.run(dbo.poll_node_status())


if __name__ == '__main__':
    main()
