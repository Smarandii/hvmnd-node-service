import pymongo
from .utils import get_system_info
from .config import MONGO_URI
import socket


def save_or_update_ngrok_url(url):
    client = pymongo.MongoClient(MONGO_URI)
    db = client["new_database"]
    collection = db["nodes"]
    machine_id = socket.gethostname()
    system_info = get_system_info()
    collection.update_one({"machine_id": machine_id},
                          {"$set": {"update_password_webhook": url, **system_info}},
                          upsert=True)
    client.close()
    print("Ngrok url updated")
