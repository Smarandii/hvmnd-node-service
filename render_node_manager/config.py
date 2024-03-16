import pathlib
import os

# Configuration settings
AUTH_TOKEN = "YourSecretToken"
PATH_TO_ANY_DESK = pathlib.Path(r"C:\Program Files (x86)\AnyDesk\AnyDesk.exe")
PATH_TO_PW_FILE = pathlib.Path(r"C:\Program Files (x86)\AnyDesk\file.txt")
NGROK_AUTHTOKEN = '2ETJzIGCEuQ8aJaGWju3nA4sswz_6xeXM7qFqhNvBXCAL8pKZ'
MONGO_URI = "mongodb+srv://admin:WIyniFnVBpcbG1pJ@cluster0.aaaafpm.mongodb.net/?retryWrites=true&w=majority"

os.environ['NGROK_AUTHTOKEN'] = NGROK_AUTHTOKEN
