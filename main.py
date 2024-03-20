# coding=utf-8
import ngrok
from render_node_manager.app import app
from render_node_manager.db_operations import save_or_update_ngrok_url
from pyuac import main_requires_admin
import Tkinter as tk
import tkMessageBox as messagebox


@main_requires_admin
def main():
    app.run(port=5000, debug=False)


if __name__ == '__main__':
    listener = ngrok.connect(5000, authtoken_from_env=True)
    print(f"Ingress established at {listener.url()}")
    save_or_update_ngrok_url(listener.url())
    main()

    root = tk.Tk()


    def on_closing():
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            root.destroy()


    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
