    from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from datetime import datetime, date
import random
import string

from .models import Student, OTP, Attendance, OTPValidation, AdminCredentials

# Utility functions
def generate_otp(length=6):
    """Generate a random OTP of specified length"""
    characters = string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def get_or_create_admin():
    """Get or create default admin credentials"""
    admin, created = AdminCredentials.objects.get_or_create(
        username='admin',
        defaults={'password': 'admin123'}
    )
    return admin

# Home page
def home(request):
    """Home page with login options"""
    return render(request, 'vtracksmart/home.html')

# Student views
def student_login(request):
    """Student login page"""
    if request.method == 'POST':
        userid = request.POST.get('userid')
        password = request.POST.get('password')
        
        try:
            student = Student.objects.get(userid=userid, password=password)
            request.session['student_id'] = student.id
            request.session['student_name'] = student.name
            request.session['is_student'] = True
            return redirect('student_dashboard')
        except Student.DoesNotExist:
            messages.error(request, 'Invalid credentials. Please try again.')
    
    return render(request, 'vtracksmart/student_login.html')

def student_dashboard(request):
    """Student dashboard"""
    if not request.session.get('is_student'):
        return redirect('student_login')
    
    student_id = request.session.get('student_id')
    student = get_object_or_404(Student, id=student_id)
    
    context = {
        'student': student,
        'student_name': request.session.get('student_name')
    }
    return render(request, 'vtracksmart/student_dashboard.html', context)

def mark_attendance(request):
    """Mark attendance with OTP"""
    if not request.session.get('is_student'):
        return redirect('student_login')
    
    if request.method == 'POST':
        otp_input = request.POST.get('otp')
        student_id = request.session.get('student_id')
        student = get_object_or_404(Student, id=student_id)
        
        # Validate OTP
        try:
            active_otp = OTP.objects.filter(is_active=True).latest('created_at')
            if active_otp.otp == otp_input:
                # Mark attendance for today
                today = date.today()
                attendance, created = Attendance.objects.get_or_create(
                    student=student,
                    date=today,
                    defaults={'present': True}
                )
                
                if created:
                    messages.success(request, '✅ Attendance marked successfully for today!')
                    # Log successful validation
                    OTPValidation.objects.create(otp=otp_input, success=True)
                else:
                    messages.info(request, 'Attendance already marked for today.')
            else:
                messages.error(request, '❌ Invalid OTP. Please check and try again.')
                # Log failed validation
                OTPValidation.objects.create(otp=otp_input, success=False)
        except OTP.DoesNotExist:
            messages.error(request, '❌ No active OTP found. Please contact your teacher.')
            OTPValidation.objects.create(otp=otp_input, success=False)
    
    return render(request, 'vtracksmart/mark_attendance.html')

def student_attendance_history(request):
    """View student's attendance history"""
    if not request.session.get('is_student'):
        return redirect('student_login')
    
    student_id = request.session.get('student_id')
    student = get_object_or_404(Student, id=student_id)
    
    attendance_records = Attendance.objects.filter(student=student).order_by('-date')
    
    context = {
        'student': student,
        'attendance_records': attendance_records
    }
    return render(request, 'vtracksmart/student_attendance_history.html', context)

# Admin views
def admin_login(request):
    """Admin login page"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        try:
            admin = AdminCredentials.objects.get(username=username, password=password)
            request.session['admin_id'] = admin.id
            request.session['admin_username'] = admin.username
            request.session['is_admin'] = True
            return redirect('admin_dashboard')
        except AdminCredentials.DoesNotExist:
            messages.error(request, 'Invalid admin credentials.')
    
    return render(request, 'vtracksmart/admin_login.html')

def admin_dashboard(request):
    """Admin dashboard"""
    if not request.session.get('is_admin'):
        return redirect('admin_login')
    
    # Get current OTP
    try:
        current_otp = OTP.objects.filter(is_active=True).latest('created_at')
    except OTP.DoesNotExist:
        current_otp = None
    
    # Get statistics
    total_students = Student.objects.count()
    today_attendance = Attendance.objects.filter(date=date.today()).count()
    
    context = {
        'admin_username': request.session.get('admin_username'),
        'current_otp': current_otp,
        'total_students': total_students,
        'today_attendance': today_attendance
    }
    return render(request, 'vtracksmart/admin_dashboard.html', context)

def generate_new_otp(request):
    """Generate a new OTP"""
    if not request.session.get('is_admin'):
        return redirect('admin_login')
    
    if request.method == 'POST':
        # Deactivate all previous OTPs
        OTP.objects.filter(is_active=True).update(is_active=False)
        
        # Generate new OTP
        new_otp = generate_otp()
        OTP.objects.create(otp=new_otp, is_active=True)
        
        messages.success(request, f'New OTP generated: {new_otp}')
    
    return redirect('admin_dashboard')

def manage_students(request):
    """Manage students"""
    if not request.session.get('is_admin'):
        return redirect('admin_login')
    
    students = Student.objects.all().order_by('name')
    
    context = {
        'students': students
    }
    return render(request, 'vtracksmart/manage_students.html', context)

def add_student(request):
    """Add new student"""
    if not request.session.get('is_admin'):
        return redirect('admin_login')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        department = request.POST.get('department')
        section = request.POST.get('section')
        userid = request.POST.get('userid')
        password = request.POST.get('password')
        
        if all([name, department, section, userid, password]):
            try:
                Student.objects.create(
                    name=name,
                    department=department,
                    section=section,
                    userid=userid,
                    password=password
                )
                messages.success(request, f'✅ Student {name} added successfully!')
                return redirect('manage_students')
            except Exception as e:
                messages.error(request, f'❌ Error adding student: {str(e)}')
        else:
            messages.error(request, '❌ All fields are required.')
    
    return render(request, 'vtracksmart/add_student.html')

def delete_student(request, student_id):
    """Delete student"""
    if not request.session.get('is_admin'):
        return redirect('admin_login')
    
    student = get_object_or_404(Student, id=student_id)
    
    if request.method == 'POST':
        student_name = student.name
        student.delete()
        messages.success(request, f'✅ Student {student_name} deleted successfully!')
        return redirect('manage_students')
    
    context = {'student': student}
    return render(request, 'vtracksmart/delete_student.html', context)

def view_all_attendance(request):
    """View all attendance records"""
    if not request.session.get('is_admin'):
        return redirect('admin_login')
    
    attendance_records = Attendance.objects.select_related('student').order_by('-date', 'student__name')
    
    context = {
        'attendance_records': attendance_records
    }
    return render(request, 'vtracksmart/view_all_attendance.html', context)

def change_admin_credentials(request):
    """Change admin credentials"""
    if not request.session.get('is_admin'):
        return redirect('admin_login')
    
    if request.method == 'POST':
        new_username = request.POST.get('username')
        new_password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if new_password != confirm_password:
            messages.error(request, '❌ Passwords do not match.')
        elif all([new_username, new_password]):
            admin_id = request.session.get('admin_id')
            admin = get_object_or_404(AdminCredentials, id=admin_id)
            admin.username = new_username
            admin.password = new_password
            admin.save()
            
            # Update session
            request.session['admin_username'] = new_username
            messages.success(request, '✅ Admin credentials updated successfully!')
            return redirect('admin_dashboard')
        else:
            messages.error(request, '❌ All fields are required.')
    
    return render(request, 'vtracksmart/change_admin_credentials.html')

# Logout views
def student_logout(request):
    """Student logout"""
    request.session.flush()
    messages.success(request, 'Logged out successfully!')
    return redirect('home')

def admin_logout(request):
    """Admin logout"""
    request.session.flush()
    messages.success(request, 'Logged out successfully!')
    return redirect('home')