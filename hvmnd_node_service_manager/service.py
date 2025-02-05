import pathlib
import time
import socket
import subprocess
from .utils import generate_password
from hvmnd_api_client import APIClient
from hvmnd_node_service_manager import logger
from hvmnd_node_service_manager.utils import send_telegram_message
from .config import (
    HVMND_API_TOKEN,
    HVMND_API_CLIENT_BASE_URL,
    ALERT_BOT_TOKEN,
    ADMIN_CHAT_ID,
    PATH_TO_PW_FILE,
    UPDATE_PW_POWERSHELL_COMMAND,
    PATH_TO_ANY_DESK,
    RESTARTING_DISABLED
)


class HVMNDNodeService:
    def __init__(self):
        self.hac = APIClient(base_url=HVMND_API_CLIENT_BASE_URL, api_token=HVMND_API_TOKEN)
        self.machine_id = socket.gethostname()
        self.node_service_version = 'v9.0.1'
        self.current_any_desk_password = None
        self._log(
            log_message=f"{self.machine_id} Node initialized {self.node_service_version}",
            alert_message=f"{self.machine_id} Node initialized {self.node_service_version}",
            log_level=logger.info
        )
        self.initialize_new_node()

    def _log(self, alert_message, log_message, log_level):
        send_telegram_message(
            token=ALERT_BOT_TOKEN,
            chat_id=ADMIN_CHAT_ID,
            message=f"{self.node_service_version} - {alert_message}"
        )
        log_level(f"{self.node_service_version} - {log_message}")

    @staticmethod
    def _generate_node_info_string(node):
        return f"{node['machine_id']} {node['id']} {node['any_desk_address']}"

    def initialize_new_node(self):
        any_desk_address = self.__get_any_desk_address()

        node_api_response = self.hac.get_nodes(machine_id=self.machine_id)
        if node_api_response['success']:
            # Node already exists
            node = node_api_response['data'][0]
            node['any_desk_address'] = any_desk_address
            node['status'] = 'available' if not node['status'] == 'occupied' else None
            self.hac.update_node(node)
            return True

        any_desk_password = self.__update_any_desk_password()

        create_node_api_response = self.hac.create_node(
            any_desk_address=any_desk_address,
            any_desk_password=any_desk_password,
            status='just_created',
            machine_id=self.machine_id
        )

        if not create_node_api_response['success']:
            self._log(
                alert_message=f"Failed to initialize new node with machine_id: {self.machine_id}."
                              f"{create_node_api_response['error']}",
                log_message=f"Failed to initialize new node with machine_id: {self.machine_id}."
                            f"{create_node_api_response['error']}",
                log_level=logger.info
            )
            return False

        self._log(
            alert_message=f"{self.machine_id} {create_node_api_response['message']}",
            log_message=f"{self.machine_id} {create_node_api_response['message']}",
            log_level=logger.info
        )
        return True

    def startup_node(self):
        """
        This method is called right before node restarts
        or first thing after hvmnd-node-service is installed and started
        """
        try:
            node_api_response = self.hac.get_nodes(machine_id=self.machine_id)

            if not node_api_response['success']:
                self._log(
                    alert_message=f"Failed to startup node with machine_id: {self.machine_id}. "
                                  f"{node_api_response['error']}",
                    log_message=f"Failed to startup node with machine_id: {self.machine_id}. "
                                f"{node_api_response['error']}",
                    log_level=logger.info
                )

                self.startup_node()

            if len(node_api_response['data']) > 1:
                self._log(
                    alert_message=f"Multiple nodes with same machine_id: {self.machine_id}."
                                  f"{node_api_response['data']}",
                    log_message=f"Multiple nodes with same machine_id: {self.machine_id}."
                                f"{node_api_response['data']}",
                    log_level=logger.info
                )
                return

            node = node_api_response['data'][0]

            node['machine_id'] = self.machine_id
            if self.current_any_desk_password:
                node['any_desk_password'] = self.current_any_desk_password
            if node['status'] == 'restarting' and not node['status'] == 'occupied':
                node['status'] = 'available'
            if node['status'] == 'restarting' and node['status'] == 'occupied':
                node['status'] = 'occupied'
            else:
                pass

            self.hac.update_node(node)

            self._log(
                alert_message=f"{HVMNDNodeService._generate_node_info_string(node)} "
                              f"startup node completed successfully...",
                log_message=f"{HVMNDNodeService._generate_node_info_string(node)} "
                            f"startup node completed successfully...",
                log_level=logger.info
            )
        except Exception as e:
            self._log(
                alert_message=f"Failed to startup node with machine_id: {self.machine_id}."
                              f"{e}",
                log_message=f"Failed to startup node with machine_id: {self.machine_id}."
                            f"{e}",
                log_level=logger.info
            )
            return False

    def poll_node_status(self):
        old_status = None
        while True:
            try:
                node_response = self.hac.get_nodes(machine_id=self.machine_id)
                node = node_response['data'][0]

                logger.info(f"old_status: {old_status} | node['status']= {node['status']}")
                if node and (old_status is None or node["status"] != old_status):
                    self.__handle_node_status_change(node, old_status)
                    old_status = node['status']
                time.sleep(5)
            except Exception as e:
                if not node_response['success']:
                    self._log(
                        alert_message=f"{self.machine_id} - {node_response['error']}",
                        log_message=f"{self.machine_id} - {node_response['error']}",
                        log_level=logger.error
                    )
                else:
                    self._log(
                        alert_message=f"{self.machine_id} Error in poll_node_status: {e}",
                        log_message=f"{self.machine_id} Error in poll_node_status: {e}",
                        log_level=logger.error
                    )
                time.sleep(5)

    def __handle_node_status_change(self, node, old_status):
        self._log(
            alert_message=f"Node {HVMNDNodeService._generate_node_info_string(node)} "
                          f"shifted from {old_status} to {node['status']}",
            log_message=f"Node {HVMNDNodeService._generate_node_info_string(node)} "
                        f"shifted from {old_status} to {node['status']}",
            log_level=logger.info
        )

        if node['status'] == 'need_to_update_password':
            self.__update_password_and_notify_user(node)
        elif node['status'] == 'restarting':
            self.__update_any_desk_password()
            node['any_desk_password'] = self.current_any_desk_password
            self.hac.update_node(node)
            self.__restart_node()
        elif node['status'] == 'update_node_service':
            self.__update_node_service()

    def __update_password_and_notify_user(self, node):
        web_app_rent_session_response = self.hac.get_rent_session(
            node_id=node['id'],
            status='active',
            platform='web_app'
        )
        telegram_rent_session_response = self.hac.get_rent_session(
            node_id=node['id'],
            status='active',
            platform='telegram'
        )

        rent_session = None
        renter = None
        platform = None
        new_password = self.__update_any_desk_password()

        if web_app_rent_session_response['success']:
            platform = 'webapp'
            rent_session = web_app_rent_session_response['data'][0]
            user_api_response = self.hac.get_users(
                id_=rent_session['renter'],
                platform=platform
            )
            if user_api_response['success']:
                renter = user_api_response['data'][0]
            notification_text = (f"Node awaits you.\n"
                                 f"AnyDesk address: {node['any_desk_address']}\n"
                                 f"AnyDesk password: {new_password}")

        if telegram_rent_session_response['success']:
            platform = 'telegram'
            rent_session = telegram_rent_session_response['data'][0]
            user_api_response = self.hac.get_users(
                id_=rent_session['renter'],
                platform=platform
            )
            if user_api_response['success']:
                renter = user_api_response['data'][0]
            notification_text = (f"AnyDesk адрес: `{node['any_desk_address']}`\n"
                                 f"AnyDesk пароль: `{new_password}`")

        if rent_session and renter and platform:
            node['any_desk_password'] = new_password
            node['status'] = 'occupied'
            self.hac.update_node(node)
            self.hac.create_notification(
                user_id=renter['id'],
                notification_text=notification_text,
                notification_platform=platform
            )
        else:
            node['any_desk_password'] = new_password
            node['status'] = 'available'
            self.hac.update_node(node)

    def __get_any_desk_address(self):
        try:
            result = subprocess.run(
                args=[PATH_TO_ANY_DESK, "--get-id"],
                capture_output=True,
                text=True,
                encoding="cp866"
            )

            if result.returncode != 0:
                error_msg = f"Failed to get AnyDesk address. Error: {result.stderr}"
                self._log(alert_message=error_msg, log_message=error_msg, log_level=logger.error)
                return None

            # Extract the AnyDesk ID from the output
            any_desk_address = result.stdout.strip()
            return any_desk_address
        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to run batch script: {e}"
            self._log(alert_message=error_msg, log_message=error_msg, log_level=logger.error)
        except Exception as e:
            error_msg = f"Unexpected error while getting AnyDesk address: {e}"
            self._log(alert_message=error_msg, log_message=error_msg, log_level=logger.error)

    def __update_any_desk_password(self):
        new_password = generate_password()
        self.current_any_desk_password = new_password
        with open(PATH_TO_PW_FILE, "w") as pwd_file:
            pwd_file.write(new_password)
        try:
            command = ["powershell.exe", "-ExecutionPolicy", "Unrestricted", "-Command", UPDATE_PW_POWERSHELL_COMMAND]
            process = subprocess.run(command, capture_output=True, text=True)
            if process.returncode != 0:
                error_msg = f"Failed to update password: {process.stderr}"
                self._log(alert_message=error_msg, log_message=error_msg, log_level=logger.error)
                return ''
            self._log(
                alert_message=f"{self.machine_id} - new password: {new_password}",
                log_message=f"{self.machine_id} - new password!",
                log_level=logger.info
            )
            return new_password
        except subprocess.CalledProcessError as e:
            error_msg = f"{self.machine_id} Failed to update password: {e}"
            self._log(alert_message=error_msg, log_message=error_msg, log_level=logger.info)

    def __restart_node(self):
        if RESTARTING_DISABLED:
            self._log(
                alert_message=f"{self.machine_id} RESTART WAS CALLED",
                log_message=f"{self.machine_id} RESTART WAS CALLED",
                log_level=logger.info
            )
            self.initialize_new_node()
            self.startup_node()

        try:
            command = ["powershell.exe", "-Command", "Restart-Computer -Force"]
            process = subprocess.run(command)
            if process.returncode != 0:
                error_msg = f"Failed to restart node: {process.stderr}"
                self._log(alert_message=error_msg, log_message=error_msg, log_level=logger.error)
        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to restart node: {e}"
            self._log(alert_message=error_msg, log_message=error_msg, log_level=logger.error)

    def __update_node_service(self):
        try:
            current_dir = pathlib.Path(__file__).parent
            project_root = current_dir.parent
            batch_file = project_root / "hvmnd_node_service_update.bat"
            log_file = project_root / "update_node.log"

            if not batch_file.exists():
                error_msg = f"Batch file not found: {batch_file}"
                self._log(alert_message=error_msg, log_message=error_msg, log_level=logger.error)
                return

            command = ["cmd.exe", "/c", str(batch_file)]
            process = subprocess.run(
                command,
                cwd=str(project_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )

            if process.returncode == 0:
                success_msg = f"Node service updated successfully:\n{process.stdout}"
                self._log(alert_message=success_msg, log_message=success_msg, log_level=logger.info)
            else:
                error_msg = (
                    f"Failed to update node service.\n"
                    f"Return Code: {process.returncode}\n"
                    f"STDOUT: {process.stdout}\n"
                    f"STDERR: {process.stderr}"
                )
                self._log(alert_message=error_msg, log_message=error_msg, log_level=logger.error)

                # Send the log file via Telegram if it exists
                if log_file.exists():
                    with open(log_file, "r", encoding="utf-8") as f:
                        log_content = f.read()
                    truncated_log = log_content[-4000:]  # Telegram limit
                    send_telegram_message(
                        token=ALERT_BOT_TOKEN,
                        chat_id=ADMIN_CHAT_ID,
                        message=f"Node update failed. Log:\n{truncated_log}"
                    )
        except Exception as e:
            error_msg = f"Exception during update: {e}"
            self._log(alert_message=error_msg, log_message=error_msg, log_level=logger.error)

            # Send log file content if available
            if log_file.exists():
                with open(log_file, "r", encoding="utf-8") as f:
                    log_content = f.read()
                truncated_log = log_content[-4000:]
                send_telegram_message(
                    token=ALERT_BOT_TOKEN,
                    chat_id=ADMIN_CHAT_ID,
                    message=f"Exception during update. Log:\n{truncated_log}"
                )
