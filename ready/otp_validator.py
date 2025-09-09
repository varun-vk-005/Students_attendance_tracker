from pymongo import MongoClient
from datetime import datetime, timedelta

# MongoDB connection
MONGO_URI = "mongodb+srv://adminvarun:TMJ9b5E9u2jMF32c@clusterstarter.rx0km.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI)
db = client["otp_db"]
otp_collection = db["otps"]
validation_collection = db["validations"]

def validate_otp(input_otp):
    """
    Validate the provided OTP against the active OTP in the database
    Returns True if valid, False otherwise
    """
    record = otp_collection.find_one({"_id": "active_otp"})
    if record and record.get("otp") == input_otp:
        # Log successful validation
        validation_collection.insert_one({
            "otp": input_otp,
            "validated_at": datetime.now(),
            "success": True
        })
        return True
    else:
        # Log failed validation attempt
        validation_collection.insert_one({
            "otp": input_otp,
            "validated_at": datetime.now(),
            "success": False
        })
        return False

def get_validation_history(limit=10):
    """Get recent OTP validation history"""
    return list(validation_collection.find().sort("validated_at", -1).limit(limit))

def clear_expired_otps(expiry_hours=24):
    """Clear OTPs that have been active for more than the specified hours"""
    expiry_time = datetime.now() - timedelta(hours=expiry_hours)
    
    # Find OTPs older than expiry time
    result = otp_collection.delete_many({
        "created_at": {"$lt": expiry_time}
    })
    
    return result.deleted_count

if __name__ == "__main__":
    # For testing purposes
    test_otp = input("Enter OTP to validate: ").strip()
    if validate_otp(test_otp):
        print("OTP is valid.")
    else:
        print("Invalid OTP.")