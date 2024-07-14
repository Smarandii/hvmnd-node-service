import time
import socket
import asyncpg
import subprocess
from .config import PG_URL, bot_token, token, chat_id, PATH_TO_PW_FILE, UPDATE_PW_POWERSHELL_COMMAND
from .utils import generate_password
from render_node_manager.utils import send_telegram_message


class DBOperations:
    def __init__(self):
        self.db_uri = PG_URL
        self.machine_id = socket.gethostname()
        send_telegram_message(token=token, chat_id=chat_id, message=str(f"{socket.gethostname()} Node initialized"))

    async def startup_node(self):
        new_password = generate_password()
        await self.__update_any_desk_password(new_password)
        conn = await asyncpg.connect(self.db_uri)
        await conn.execute('''
            INSERT INTO nodes (machine_id, any_desk_password, status)
            VALUES ($1, $2, $3)
            ON CONFLICT (machine_id) DO UPDATE
            SET any_desk_password = EXCLUDED.any_desk_password, status = EXCLUDED.status
        ''', self.machine_id, new_password, 'available')
        await conn.close()
        send_telegram_message(token=token, chat_id=chat_id, message=str(f"{socket.gethostname()} Node available - {new_password}"))

    async def poll_node_status(self):
        old_status = None
        while True:
            try:
                conn = await asyncpg.connect(self.db_uri)
                node = await conn.fetchrow('SELECT * FROM nodes WHERE machine_id = $1', self.machine_id)
                await conn.close()

                if node:
                    if old_status is None or node["status"] != old_status:
                        if node['status'] == 'need_to_update_password':
                            new_password = generate_password()
                            await self.__update_any_desk_password(new_password)
                            if node['renter'] is not None:
                                conn = await asyncpg.connect(self.db_uri)
                                await conn.execute('''
                                    UPDATE nodes
                                    SET any_desk_password = $1, status = $2
                                    WHERE machine_id = $3
                                ''', new_password, 'occupied', self.machine_id)
                                await conn.close()

                                send_telegram_message(
                                    token=bot_token,
                                    chat_id=node['renter'],
                                    message=f"AnyDesk адрес: {node['any_desk_address']}\n"
                                            f"AnyDesk пароль: {new_password}"
                                )
                            else:
                                conn = await asyncpg.connect(self.db_uri)
                                await conn.execute('''
                                    UPDATE nodes
                                    SET any_desk_password = $1, status = $2
                                    WHERE machine_id = $3
                                ''', new_password, 'available', self.machine_id)
                                await conn.close()
                        if node['status'] == 'restarting':
                            await self.__restart_node()

                        log_message = f"Node {node['old_id']} shifted from {old_status} to {node['status']}"
                        print(log_message)
                        old_status = node['status']
                        time.sleep(5)
            except Exception as e:
                send_telegram_message(token=token, chat_id=chat_id, message=str(e.args))
                time.sleep(5)
            time.sleep(5)

    async def __update_any_desk_password(self, new_password: str):
        with open(PATH_TO_PW_FILE, "w") as pwd_file:
            pwd_file.write(new_password)
        try:
            command = ["powershell.exe", "-ExecutionPolicy", "Unrestricted", "-Command", UPDATE_PW_POWERSHELL_COMMAND]
            process = subprocess.run(command, capture_output=True, text=True)
            if process.returncode == 0:
                return new_password
            else:
                send_telegram_message(token=token, chat_id=chat_id, message=str({"error": "Failed to update password", "details": process.stderr}))
                return {"error": "Failed to update password", "details": process.stderr}
        except subprocess.CalledProcessError as e:
            send_telegram_message(token=token, chat_id=chat_id, message=str({"error": "Failed to update password", "details": str(e)}))
            return {"error": "Failed to update password", "details": str(e)}

    async def __restart_node(self):
        try:
            command = ["powershell.exe", "-Command", "Restart-Computer -Force"]
            process = subprocess.run(command)
            if process.returncode == 0:
                return {"restarted": True}
            else:
                send_telegram_message(token=token, chat_id=chat_id, message=str({"error": "Failed to restart node", "details": process.stderr}))
                return {"error": "Failed to restart node", "details": process.stderr}
        except subprocess.CalledProcessError as e:
            send_telegram_message(token=token, chat_id=chat_id, message=str({"error": "Failed to restart node", "details": str(e)}))
            return {"error": "Failed to restart node", "details": str(e)}

    def __del__(self):
        pass  # No need to explicitly close connections, asyncpg handles it

# Usage example (make sure to run in an async context)
# db_operations = DBOperations()
# asyncio.run(db_operations.startup_node())
# asyncio.run(db_operations.poll_node_status())
