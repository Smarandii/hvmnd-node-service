import ngrok
from render_node_manager.app import app
from render_node_manager.db_operations import save_or_update_ngrok_url

if __name__ == '__main__':
    listener = ngrok.connect(5000, authtoken_from_env=True)
    print(f"Ingress established at {listener.url()}")
    save_or_update_ngrok_url(listener.url())
    app.run(port=5000, debug=True)
