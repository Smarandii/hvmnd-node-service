import time
import socket
import asyncpg
import subprocess
from .utils import generate_password
from render_node_manager import logger
from render_node_manager.utils import send_telegram_message
from .config import (
    PG_URL,
    ALERT_BOT_TOKEN,
    ADMIN_CHAT_ID,
    PATH_TO_PW_FILE,
    UPDATE_PW_POWERSHELL_COMMAND
)


class DBOperations:
    def __init__(self):
        self.db_uri = PG_URL
        self.machine_id = socket.gethostname()
        logger.info(f"{self.machine_id} Node initialized")
        send_telegram_message(token=ALERT_BOT_TOKEN, chat_id=ADMIN_CHAT_ID, message=f"{self.machine_id} Node initialized")

    def _log(self, alert_message, log_message, log_level):
        send_telegram_message(
            token=ALERT_BOT_TOKEN,
            chat_id=ADMIN_CHAT_ID,
            message=alert_message
        )
        log_level(log_message)

    async def startup_node(self):
        node = await self.__fetch_db_row('SELECT * FROM nodes WHERE machine_id = $1', self.machine_id)
        if not node['renter']:
            new_password = await self.__update_any_desk_password()
            await self.__execute_db_query('''
                INSERT INTO nodes (machine_id, any_desk_password, status)
                VALUES ($1, $2, $3)
                ON CONFLICT (machine_id) DO UPDATE
                SET any_desk_password = EXCLUDED.any_desk_password, status = EXCLUDED.status
            ''', self.machine_id, new_password, 'available')

            self._log(
                alert_message=f"{node['old_id']} {node['id']} {node['any_desk_address']} {self.machine_id} Node is available - {new_password}",
                log_message=f"{node['old_id']} {node['id']} {node['any_desk_address']} {self.machine_id} Node is available...",
                log_level=logger.info
            )

    async def poll_node_status(self):
        old_status = None
        while True:
            try:
                node = await self.__fetch_db_row('SELECT * FROM nodes WHERE machine_id = $1', self.machine_id)
                logger.info(f"old_status: {old_status} | node['status']= {node['status']}")
                if node and (old_status is None or node["status"] != old_status):
                    await self.__handle_node_status_change(node, old_status)
                    old_status = node['status']
                time.sleep(5)
            except Exception as e:
                logger.error(f"Error in poll_node_status: {e}")
                send_telegram_message(token=ALERT_BOT_TOKEN, chat_id=ADMIN_CHAT_ID, message=str(e))
                time.sleep(5)

    async def __handle_node_status_change(self, node, old_status):
        if node['status'] == 'need_to_update_password':
            await self.__update_password_and_notify_user(node)
        elif node['status'] == 'restarting':
            await self.__restart_node()
        elif node['status'] == 'update_node_service':
            await self.__update_node_service()

        logger.info(f"Node {node['old_id']} shifted from {old_status} to {node['status']}")

    async def __update_password_and_notify_user(self, node):
        new_password = await self.__update_any_desk_password()
        if node['renter']:
            user = await self.__fetch_db_row('SELECT telegram_id FROM users WHERE id = $1', node['renter'])
            if user:
                await self.__execute_db_query('''
                    UPDATE nodes SET any_desk_password = $1, status = $2 WHERE machine_id = $3
                ''', new_password, 'occupied', self.machine_id)

                await self.__execute_db_query('''
                    INSERT INTO notifications (user_id, notification_text, notification_platform)
                    VALUES ($1, $2, 'web_app'), ($1, $3, 'telegram')
                ''', node['renter'],
                      f"Node awaits you.\nAnyDesk address: {node['any_desk_address']}\nAnyDesk password: {new_password}",
                      f"AnyDesk адрес: `{node['any_desk_address']}`\nAnyDesk пароль: `{new_password}`")
        else:
            await self.__execute_db_query('''
                UPDATE nodes SET any_desk_password = $1, status = $2 WHERE machine_id = $3
            ''', new_password, 'available', self.machine_id)

    async def __update_any_desk_password(self):
        new_password = generate_password()
        with open(PATH_TO_PW_FILE, "w") as pwd_file:
            pwd_file.write(new_password)
        try:
            command = ["powershell.exe", "-ExecutionPolicy", "Unrestricted", "-Command", UPDATE_PW_POWERSHELL_COMMAND]
            process = subprocess.run(command, capture_output=True, text=True)
            if process.returncode != 0:
                error_msg = f"Failed to update password: {process.stderr}"
                self._log(alert_message=error_msg, log_message=error_msg, log_level=logger.error)
                return ''
            return new_password
        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to update password: {e}"
            self._log(alert_message=error_msg, log_message=error_msg, log_level=logger.info)

    async def __restart_node(self):
        try:
            command = ["powershell.exe", "-Command", "Restart-Computer -Force"]
            process = subprocess.run(command)
            if process.returncode != 0:
                error_msg = f"Failed to restart node: {process.stderr}"
                self._log(alert_message=error_msg, log_message=error_msg, log_level=logger.error)
        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to restart node: {e}"
            self._log(alert_message=error_msg, log_message=error_msg, log_level=logger.error)

    async def __update_node_service(self):
        try:
            command = ["cmd.exe", "/c", "update_node_by_request.bat"]
            process = subprocess.run(command, capture_output=True, text=True)
            if process.returncode != 0:
                error_msg = (
                    f"Failed to update node service. "
                    f"Error code: {process.returncode}\n"
                    f"STDOUT: {process.stdout}\n"
                    f"STDERR: {process.stderr}"
                )
                self._log(alert_message=error_msg, log_message=error_msg, log_level=logger.error)

            if process.returncode == 0:
                success_msg = f"Node service updated successfully:\n{process.stdout}"
                self._log(alert_message=success_msg, log_message=success_msg, log_level=logger.info)
            else:
                error_msg = f"Failed to update node service. Error code: {process.returncode}\n{process.stderr}"
                self._log(alert_message=error_msg, log_message=error_msg, log_level=logger.error)
        except Exception as e:
            error_msg = f"Exception occurred while updating node service: {e}"
            self._log(alert_message=error_msg, log_message=error_msg, log_level=logger.error)

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
