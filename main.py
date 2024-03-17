# coding=utf-8
import ngrok
from render_node_manager.app import app
from render_node_manager.db_operations import save_or_update_ngrok_url
from pyuac import main_requires_admin


@main_requires_admin
def main():
    listener = ngrok.connect(5000, authtoken_from_env=True)
    print(f"Ingress established at {listener.url()}")
    save_or_update_ngrok_url(listener.url())
    app.run(port=5000, debug=True)


if __name__ == '__main__':
    main()
