# coding=utf-8
from pyuac import main_requires_admin
from render_node_manager.db_operations import DBOperations
from render_node_manager.utils import add_to_system_path
from render_node_manager.config import PATH_TO_ANY_DESK


@main_requires_admin
def main():
    add_to_system_path(PATH_TO_ANY_DESK.parent)
    dbo = DBOperations()
    dbo.startup_node()
    dbo.poll_node_status()


if __name__ == '__main__':
    main()


