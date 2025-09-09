import os
from datetime import datetime
import time

# Import our custom modules
from otp_generator import generate_otp, store_otp, get_current_otp
from student_details_storer import (
    store_student, get_student, delete_student, 
    update_student, get_all_students, mark_attendance, 
    get_student_attendance
)
from otp_validator import validate_otp
from admin_manager import get_admin_credentials, update_admin_credentials, validate_admin

# Global variables
current_user = None
is_admin = False

def clear_screen():
    """Clear the console screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title):
    """Print a formatted header"""
    clear_screen()
    print("=" * 50)
    print(f"{title:^50}")
    print("=" * 50)
    print()

def login():
    """Handle user login (both admin and student)"""
    global current_user, is_admin
    
    print_header("VTrackSmart - Login")
    
    print("1. Student Login")
    print("2. Admin Login")
    print("3. Exit")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        # Student login
        userid = input("Enter your User ID: ").strip()
        password = input("Enter your Password: ").strip()
        
        student = get_student(userid, password)
        if student:
            current_user = student
            is_admin = False
            print("\nLogin successful!")
            time.sleep(1)
            return True
        else:
            print("\nInvalid credentials. Please try again.")
            time.sleep(2)
            return False
            
    elif choice == "2":
        # Admin login
        username = input("Admin Username: ").strip()
        password = input("Admin Password: ").strip()
        
        if validate_admin(username, password):
            current_user = {"name": "Administrator", "role": "admin", "username": username}
            is_admin = True
            print("\nAdmin login successful!")
            time.sleep(1)
            return True
        else:
            print("\nInvalid admin credentials.")
            time.sleep(2)
            return False
            
    elif choice == "3":
        print("\nExiting program...")
        exit(0)
        
    else:
        print("\nInvalid choice. Please try again.")
        time.sleep(1)
        return False

def student_menu():
    """Display and handle student menu options"""
    while True:
        print_header(f"Student Dashboard - Welcome {current_user['name']}")
        
        print("1. Mark Attendance with OTP")
        print("2. View My Attendance History")
        print("3. Logout")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            mark_attendance_with_otp()
        elif choice == "2":
            view_attendance_history()
        elif choice == "3":
            print("\nLogging out...")
            time.sleep(1)
            return
        else:
            print("\nInvalid choice. Please try again.")
            time.sleep(1)

def mark_attendance_with_otp():
    """Allow student to mark attendance using OTP"""
    print_header("Mark Attendance with OTP")
    
    otp = input("Enter the OTP provided by your teacher: ").strip()
    
    if validate_otp(otp):
        # Mark attendance for today
        student_id = current_user["_id"]
        today = datetime.now().strftime("%Y-%m-%d")
        
        if mark_attendance(student_id, today):
            print("\n✅ Attendance marked successfully for today!")
        else:
            print("\n❌ Failed to mark attendance. Please try again later.")
    else:
        print("\n❌ Invalid OTP. Please check and try again.")
    
    input("\nPress Enter to continue...")

def view_attendance_history():
    """Display attendance history for the current student"""
    print_header("My Attendance History")
    
    attendance_records = get_student_attendance(current_user["_id"])
    
    if not attendance_records:
        print("No attendance records found.")
    else:
        print(f"{'Date':<15} {'Status':<10} {'Marked At':<20}")
        print("-" * 45)
        
        for record in attendance_records:
            date = record.get("date", "N/A")
            status = "Present" if record.get("present", False) else "Absent"
            marked_at = record.get("marked_at", "N/A")
            
            if isinstance(marked_at, datetime):
                marked_at = marked_at.strftime("%Y-%m-%d %H:%M:%S")
                
            print(f"{date:<15} {status:<10} {marked_at:<20}")
    
    input("\nPress Enter to continue...")

def admin_menu():
    """Display and handle admin menu options"""
    while True:
        print_header("Admin Dashboard")
        
        print("1. Generate New OTP")
        print("2. View Current OTP")
        print("3. Manage Students")
        print("4. View All Students")
        print("5. Change Admin Credentials")
        print("6. Logout")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == "1":
            generate_new_otp()
        elif choice == "2":
            view_current_otp()
        elif choice == "3":
            manage_students()
        elif choice == "4":
            view_all_students()
        elif choice == "5":
            change_admin_credentials()
        elif choice == "6":
            print("\nLogging out...")
            time.sleep(1)
            return
        else:
            print("\nInvalid choice. Please try again.")
            time.sleep(1)

def generate_new_otp():
    """Generate and store a new OTP"""
    print_header("Generate New OTP")
    
    # Generate a new OTP
    new_otp = generate_otp()
    store_otp(new_otp)
    
    print(f"New OTP generated: {new_otp}")
    print("\nThis OTP has been stored and is now active.")
    
    input("\nPress Enter to continue...")

def view_current_otp():
    """View the current active OTP"""
    print_header("Current Active OTP")
    
    current_otp = get_current_otp()
    
    if current_otp:
        print(f"Current active OTP: {current_otp}")
    else:
        print("No active OTP found. Please generate a new OTP.")
    
    input("\nPress Enter to continue...")

def manage_students():
    """Menu for student management"""
    while True:
        print_header("Student Management")
        
        print("1. Add New Student")
        print("2. Delete Student")
        print("3. Back to Admin Menu")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            add_student()
        elif choice == "2":
            delete_student_menu()
        elif choice == "3":
            return
        else:
            print("\nInvalid choice. Please try again.")
            time.sleep(1)

def add_student():
    """Add a new student to the database"""
    print_header("Add New Student")
    
    print("Please enter the following details:")
    name = input("Name: ").strip()
    department = input("Department: ").strip()
    section = input("Section: ").strip()
    userid = input("User ID: ").strip()
    password = input("Password: ").strip()
    
    if not all([name, department, section, userid, password]):
        print("\nAll fields are required. Student not added.")
    else:
        student_id = store_student(name, department, section, userid, password)
        if student_id:
            print(f"\n✅ Student added successfully with ID: {student_id}")
        else:
            print("\n❌ Failed to add student. Please try again.")
    
    input("\nPress Enter to continue...")

def delete_student_menu():
    """Delete a student from the database"""
    print_header("Delete Student")
    
    # First, display all students
    students = get_all_students()
    
    if not students:
        print("No students found in the database.")
        input("\nPress Enter to continue...")
        return
    
    print("Current Students:")
    print(f"{'ID':<24} {'Name':<20} {'Department':<15} {'Section':<10} {'User ID':<15}")
    print("-" * 85)
    
    for student in students:
        student_id = str(student.get("_id", "N/A"))
        name = student.get("name", "N/A")
        department = student.get("department", "N/A")
        section = student.get("section", "N/A")
        userid = student.get("userid", "N/A")
        
        print(f"{student_id:<24} {name:<20} {department:<15} {section:<10} {userid:<15}")
    
    print("\nEnter the ID of the student to delete, or 'cancel' to go back:")
    student_id = input("> ").strip()
    
    if student_id.lower() == 'cancel':
        return
    
    # Confirm deletion
    confirm = input(f"\nAre you sure you want to delete this student? (y/n): ").strip().lower()
    
    if confirm == 'y':
        if delete_student(student_id):
            print(f"\n✅ Student with ID '{student_id}' deleted successfully.")
        else:
            print(f"\n❌ No student found with ID '{student_id}'.")
    else:
        print("\nDeletion cancelled.")
    
    input("\nPress Enter to continue...")

def view_all_students():
    """View all students in the database"""
    print_header("All Students")
    
    students = get_all_students()
    
    if not students:
        print("No students found in the database.")
    else:
        print(f"{'ID':<24} {'Name':<20} {'Department':<15} {'Section':<10} {'User ID':<15}")
        print("-" * 85)
        
        for student in students:
            student_id = str(student.get("_id", "N/A"))
            name = student.get("name", "N/A")
            department = student.get("department", "N/A")
            section = student.get("section", "N/A")
            userid = student.get("userid", "N/A")
            
            print(f"{student_id:<24} {name:<20} {department:<15} {section:<10} {userid:<15}")
    
    input("\nPress Enter to continue...")

def change_admin_credentials():
    """Change admin username and password"""
    print_header("Change Admin Credentials")
    
    # Get current admin credentials
    admin = get_admin_credentials()
    current_username = admin.get("username")
    
    print(f"Current Username: {current_username}")
    print("\nEnter new credentials (leave blank to keep current):")
    
    # Get new username
    new_username = input("New Username: ").strip()
    if not new_username:
        new_username = current_username
        
    # Get new password with confirmation
    while True:
        new_password = input("New Password: ").strip()
        if not new_password:
            new_password = admin.get("password")
            break
            
        confirm_password = input("Confirm New Password: ").strip()
        if new_password == confirm_password:
            break
        else:
            print("\n❌ Passwords do not match. Please try again.")
    
    # Confirm changes
    print("\nReview your changes:")
    print(f"Username: {current_username} → {new_username}")
    print(f"Password: {'*' * len(admin.get('password'))} → {'*' * len(new_password)}")
    
    confirm = input("\nSave these changes? (y/n): ").strip().lower()
    
    if confirm == 'y':
        if update_admin_credentials(new_username, new_password):
            print("\n✅ Admin credentials updated successfully!")
            # Update current user with new username
            if current_user and current_user.get("role") == "admin":
                current_user["username"] = new_username
        else:
            print("\n❌ Failed to update admin credentials. Please try again later.")
    else:
        print("\nChanges cancelled.")
    
    input("\nPress Enter to continue...")

def main():
    """Main application entry point"""
    global current_user, is_admin
    
    while True:
        # Handle login
        if not login():
            continue
        
        # Route to appropriate menu based on user type
        if is_admin:
            admin_menu()
        else:
            student_menu()
        
        # Reset user state after logout
        current_user = None
        is_admin = False

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgram terminated by user.")
    except Exception as e:
        print(f"\n\nAn error occurred: {e}")
    finally:
        print("\nThank you for using VTrackSmart!")