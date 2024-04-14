import time
import socket
import pymongo
import subprocess
from .config import MONGO_URI
from .utils import generate_password
from render_node_manager.config import token, chat_id
from render_node_manager.utils import send_telegram_message
from .config import PATH_TO_PW_FILE, UPDATE_PW_POWERSHELL_COMMAND


class DBOperations:
    def __init__(self):
        self.client = pymongo.MongoClient(MONGO_URI)
        self.db = self.client["new_database"]
        self.collection = self.db["nodes"]
        self.machine_id = socket.gethostname()

    def startup_node(self):
        new_password = generate_password()
        self.__update_any_desk_password(new_password)
        self.collection.update_one(
            {"machine_id": self.machine_id},
            {
                "$set":
                    {
                        "any_desk_password": new_password,
                        "status": "available"
                    }
            },
            upsert=True
        )
        send_telegram_message(token=token, chat_id=chat_id, message=str(f"{socket.gethostname()} Node available"))

    def poll_node_status(self):
        old_status = None
        while True:
            try:
                node = self.collection.find_one({"machine_id": self.machine_id})
                if old_status is None or node["status"] != old_status:
                    if node['status'] == 'need_to_update_password':
                        new_password = generate_password()
                        password = self.__update_any_desk_password(new_password)
                        if node['renter'] is not None:
                            self.collection.update_one(
                                {"machine_id": self.machine_id},
                                {"$set": {"any_desk_password": password, "status": "occupied"}}
                            )
                        else:
                            self.collection.update_one(
                                {"machine_id": self.machine_id},
                                {"$set": {"any_desk_password": password, "status": "available"}}
                            )
                    if node['status'] == 'restarting':
                        self.__restart_node()

                    log_message = f"Node {node['old_id']} shifted from {old_status} to {node['status']}"
                    print(log_message)
                    old_status = node['status']
                    time.sleep(5)
            except Exception as e:
                send_telegram_message(token=token, chat_id=chat_id, message=str(e.args))
                time.sleep(5)
            time.sleep(5)

    def __update_any_desk_password(self, new_password: str):
        with open(PATH_TO_PW_FILE, "w") as pwd_file:
            pwd_file.write(new_password)
        try:
            command = ["powershell.exe", "-ExecutionPolicy", "Unrestricted", "-Command", UPDATE_PW_POWERSHELL_COMMAND]
            process = subprocess.run(command, capture_output=True, text=True)
            if process.returncode == 0:
                return new_password
            else:
                return {"error": "Failed to update password", "details": process.stderr}
        except subprocess.CalledProcessError as e:
            return {"error": "Failed to update password", "details": str(e)}

    def __restart_node(self):
        try:
            command = ["powershell.exe", "-Command", "Restart-Computer -Force"]
            process = subprocess.run(command)
            if process.returncode == 0:
                return {"restarted": True}
            else:
                return {"error": "Failed to restart node", "details": process.stderr}
        except subprocess.CalledProcessError as e:
            return {"error": "Failed to restart node", "details": str(e)}

    def __del__(self):
        self.client.close()
