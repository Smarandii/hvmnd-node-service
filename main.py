# coding=utf-8
from pyuac import main_requires_admin
from render_node_manager.db_operations import DBOperations


@main_requires_admin
def main():
    dbo = DBOperations()
    dbo.startup_node()
    dbo.poll_node_status()


if __name__ == '__main__':
    main()


