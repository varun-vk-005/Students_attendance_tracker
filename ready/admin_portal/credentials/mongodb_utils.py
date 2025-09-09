from pymongo import MongoClient

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "vtrack_smart"
COLLECTION_NAME = "admin_credentials"

DEFAULT_ADMIN = {
    "username": "admin",
    "password": "admin123"
}

def get_admin_credentials():
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        admin = collection.find_one({"type": "admin"})
        if not admin:
            DEFAULT_ADMIN["type"] = "admin"
            collection.insert_one(DEFAULT_ADMIN)
            return DEFAULT_ADMIN
        return admin
    except Exception as e:
        print(f"DB Error: {e}")
        return DEFAULT_ADMIN

def update_admin_credentials(username, password):
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        if collection.find_one({"type": "admin"}):
            collection.update_one({"type": "admin"}, {"$set": {"username": username, "password": password}})
        else:
            collection.insert_one({"type": "admin", "username": username, "password": password})
        return True
    except Exception as e:
        print(f"Update Error: {e}")
        return False

def validate_admin(username, password):
    admin = get_admin_credentials()
    return username == admin.get("username") and password == admin.get("password")
