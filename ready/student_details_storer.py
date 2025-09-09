from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId

# MongoDB connection
MONGO_URI = "mongodb+srv://adminvarun:TMJ9b5E9u2jMF32c@clusterstarter.rx0km.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI)
db = client["student_db"]
students_collection = db["students"]
attendance_collection = db["attendance"]

def store_student(name, department, section, userid, password):
    """Store student details in the database"""
    result = students_collection.insert_one({
        "name": name.strip(),
        "department": department.strip(),
        "section": section.strip(),
        "userid": userid.strip(),
        "password": password.strip(),
        "created_at": datetime.now()
    })
    return result.inserted_id

def get_student(userid, password=None):
    """Get student details by userid and optionally verify password"""
    query = {"userid": userid}
    if password:
        query["password"] = password
    
    return students_collection.find_one(query)

def delete_student(student_id):
    """Delete a student by ID"""
    try:
        # Try to convert to ObjectId if it's a string
        if isinstance(student_id, str):
            student_id = ObjectId(student_id)
        result = students_collection.delete_one({"_id": student_id})
        return result.deleted_count > 0
    except Exception as e:
        print(f"Error deleting student: {e}")
        return False

def update_student(student_id, update_data):
    """Update student details"""
    try:
        # Convert to ObjectId if it's a string
        if isinstance(student_id, str):
            student_id = ObjectId(student_id)
        
        result = students_collection.update_one(
            {"_id": student_id},
            {"$set": update_data}
        )
        return result.modified_count > 0
    except Exception as e:
        print(f"Error updating student: {e}")
        return False

def get_all_students():
    """Get all students from the database"""
    return list(students_collection.find())

def mark_attendance(student_id, date=None):
    """Mark attendance for a student"""
    try:
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        # Convert to ObjectId if it's a string
        if isinstance(student_id, str):
            student_id = ObjectId(student_id)
        
        # Check if student exists
        student = students_collection.find_one({"_id": student_id})
        if not student:
            return False
        
        # Mark attendance
        result = attendance_collection.update_one(
            {"student_id": student_id, "date": date},
            {"$set": {
                "student_id": student_id,
                "date": date,
                "present": True,
                "marked_at": datetime.now()
            }},
            upsert=True
        )
        return True
    except Exception as e:
        print(f"Error marking attendance: {e}")
        return False

def get_student_attendance(student_id):
    """Get attendance records for a student"""
    try:
        # Convert to ObjectId if it's a string
        if isinstance(student_id, str):
            student_id = ObjectId(student_id)
        return list(attendance_collection.find({"student_id": student_id}))
    except Exception as e:
        print(f"Error getting attendance: {e}")
        return []

if __name__ == "__main__":
    # For testing purposes
    print("Student Management Module")
    print("Available functions:")
    print("- store_student(name, department, section, userid, password)")
    print("- get_student(userid, password)")
    print("- delete_student(student_id)")
    print("- update_student(student_id, update_data)")
    print("- get_all_students()")
    print("- mark_attendance(student_id, date)")
    print("- get_student_attendance(student_id)")