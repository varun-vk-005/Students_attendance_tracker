import random
import string
from pymongo import MongoClient
from datetime import datetime

# MongoDB connection
MONGO_URI = "mongodb+srv://adminvarun:TMJ9b5E9u2jMF32c@clusterstarter.rx0km.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI)
db = client["otp_db"]
otp_collection = db["otps"]

def generate_otp(length=6):
    """Generate a random OTP of specified length"""
    characters = string.digits  # Only numbers
    otp = ''.join(random.choice(characters) for _ in range(length))
    return otp

def store_otp(otp=None):
    """Store OTP in the database. If no OTP is provided, generate a new one."""
    if otp is None:
        otp = generate_otp()
    

    
    otp_collection.update_one(
        {"_id": "active_otp"},  
        {"$set": {
            "otp": otp,
            "created_at": datetime.now()
        }},
        upsert=True
    )
    return otp

def get_current_otp():
    """Retrieve the current active OTP from the database"""
    record = otp_collection.find_one({"_id": "active_otp"})
    if record and "otp" in record:
        return record["otp"]
    return None

if __name__ == "__main__":
    # For testing purposes
    new_otp = generate_otp()
    print(f"Generated OTP: {new_otp}")
    store_otp(new_otp)
    print(f"Stored OTP: {get_current_otp()}")