import time
import socket
import asyncpg
import subprocess
from datetime import datetime
from loguru import logger
from .config import PG_URL, bot_token, token, chat_id, PATH_TO_PW_FILE, UPDATE_PW_POWERSHELL_COMMAND
from .utils import generate_password
from render_node_manager.utils import send_telegram_message


class DBOperations:
    def __init__(self):
        self.db_uri = PG_URL
        self.machine_id = socket.gethostname()
        logger.info(f"{self.machine_id} Node initialized")
        send_telegram_message(token=token, chat_id=chat_id, message=f"{self.machine_id} Node initialized")

    async def startup_node(self):
        new_password = generate_password()
        await self.__update_any_desk_password(new_password)
        await self.__execute_db_query('''
            INSERT INTO nodes (machine_id, any_desk_password, status)
            VALUES ($1, $2, $3)
            ON CONFLICT (machine_id) DO UPDATE
            SET any_desk_password = EXCLUDED.any_desk_password, status = EXCLUDED.status
        ''', self.machine_id, new_password, 'available')
        send_telegram_message(token=token, chat_id=chat_id, message=f"{self.machine_id} Node available - {new_password}")

    async def poll_node_status(self):
        old_status = None
        while True:
            try:
                node = await self.__fetch_db_row('SELECT * FROM nodes WHERE machine_id = $1', self.machine_id)
                if node and (old_status is None or node["status"] != old_status):
                    await self.__handle_node_status_change(node, old_status)
                    old_status = node['status']
                time.sleep(5)
            except Exception as e:
                logger.error(f"Error in poll_node_status: {e}")
                send_telegram_message(token=token, chat_id=chat_id, message=str(e))
                time.sleep(5)

    async def __handle_node_status_change(self, node, old_status):
        if node['status'] == 'need_to_update_password':
            await self.__update_password_and_notify_user(node)
        elif node['status'] == 'restarting':
            await self.__restart_node()

        logger.info(f"Node {node['old_id']} shifted from {old_status} to {node['status']}")

    async def __update_password_and_notify_user(self, node):
        new_password = generate_password()
        await self.__update_any_desk_password(new_password)
        if node['renter']:
            user = await self.__fetch_db_row('SELECT telegram_id FROM users WHERE id = $1', node['renter'])
            if user:
                telegram_id = user['telegram_id']
                await self.__execute_db_query('''
                    UPDATE nodes SET any_desk_password = $1, status = $2 WHERE machine_id = $3
                ''', new_password, 'occupied', self.machine_id)
                send_telegram_message(
                    token=bot_token,
                    chat_id=telegram_id,
                    message=f"AnyDesk адрес: `{node['any_desk_address']}`\nAnyDesk пароль: `{new_password}`",
                    parse_mode='MarkdownV2'
                )
        else:
            await self.__execute_db_query('''
                UPDATE nodes SET any_desk_password = $1, status = $2 WHERE machine_id = $3
            ''', new_password, 'available', self.machine_id)

    async def __update_any_desk_password(self, new_password: str):
        with open(PATH_TO_PW_FILE, "w") as pwd_file:
            pwd_file.write(new_password)
        try:
            command = ["powershell.exe", "-ExecutionPolicy", "Unrestricted", "-Command", UPDATE_PW_POWERSHELL_COMMAND]
            process = subprocess.run(command, capture_output=True, text=True)
            if process.returncode != 0:
                error_msg = f"Failed to update password: {process.stderr}"
                logger.error(error_msg)
                send_telegram_message(token=token, chat_id=chat_id, message=error_msg)
        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to update password: {e}"
            logger.error(error_msg)
            send_telegram_message(token=token, chat_id=chat_id, message=error_msg)

    async def __restart_node(self):
        try:
            command = ["powershell.exe", "-Command", "Restart-Computer -Force"]
            process = subprocess.run(command)
            if process.returncode != 0:
                error_msg = f"Failed to restart node: {process.stderr}"
                logger.error(error_msg)
                send_telegram_message(token=token, chat_id=chat_id, message=error_msg)
        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to restart node: {e}"
            logger.error(error_msg)
            send_telegram_message(token=token, chat_id=chat_id, message=error_msg)

    async def __execute_db_query(self, query, *params):
        conn = await asyncpg.connect(self.db_uri)
        try:
            await conn.execute(query, *params)
        except Exception as e:
            logger.error(f"Database query failed: {e}")
            raise
        finally:
            await conn.close()

    async def __fetch_db_row(self, query, *params):
        conn = await asyncpg.connect(self.db_uri)
        try:
            return await conn.fetchrow(query, *params)
        except Exception as e:
            logger.error(f"Database fetch failed: {e}")
            raise
        finally:
            await conn.close()
