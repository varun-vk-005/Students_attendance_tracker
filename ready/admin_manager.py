import os
import json
from pymongo import MongoClient

# MongoDB connection
MONGO_URI = "mongodb+srv://adminvarun:TMJ9b5E9u2jMF32c@clusterstarter.rx0km.mongodb.net/?retryWrites=true&w=majority"
DB_NAME = "vtrack_smart"
COLLECTION_NAME = "admin_credentials"

# Default admin credentials
DEFAULT_ADMIN = {
    "username": "admin",
    "password": "admin123"
}

def get_admin_credentials():
    """Get admin credentials from MongoDB"""
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        
        # Try to get admin credentials
        admin = collection.find_one({"type": "admin"})
        
        # If no admin credentials found, create default ones
        if not admin:
            DEFAULT_ADMIN["type"] = "admin"
            collection.insert_one(DEFAULT_ADMIN)
            return DEFAULT_ADMIN
        
        return admin
    except Exception as e:
        print(f"Error connecting to database: {e}")
        # Fallback to default credentials if database connection fails
        return DEFAULT_ADMIN

def update_admin_credentials(username, password):
    """Update admin credentials in MongoDB"""
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        
        # Check if admin credentials exist
        admin = collection.find_one({"type": "admin"})
        
        if admin:
            # Update existing credentials
            collection.update_one(
                {"type": "admin"},
                {"$set": {"username": username, "password": password}}
            )
        else:
            # Create new admin credentials
            collection.insert_one({
                "type": "admin",
                "username": username,
                "password": password
            })
        
        return True
    except Exception as e:
        print(f"Error updating admin credentials: {e}")
        return False

def validate_admin(username, password):
    """Validate admin credentials"""
    admin = get_admin_credentials()
    return username == admin.get("username") and password == admin.get("password")