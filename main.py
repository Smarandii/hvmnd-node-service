# coding=utf-8
import ngrok
from render_node_manager.app import app
from render_node_manager.db_operations import save_or_update_ngrok_url
from pyuac import main_requires_admin
from render_node_manager.utils import add_to_startup, TERMINATION_SIGNALS, signal_handler, signal


@main_requires_admin
def main():
    app.run(port=5000, debug=False)


if __name__ == '__main__':
    for sig in TERMINATION_SIGNALS:
        signal.signal(sig, signal_handler)

    add_to_startup(r"C:\Program Files (x86)\render_hive_farm_bot_node_service\main.exe")
    listener = ngrok.connect(5000, authtoken_from_env=True)
    print(f"Ingress established at {listener.url()}")
    save_or_update_ngrok_url(listener.url())
    main()
