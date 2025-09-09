from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

class Student(models.Model):
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=50)
    section = models.CharField(max_length=10)
    userid = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.userid})"
    
    class Meta:
        db_table = 'students'

class OTP(models.Model):
    otp = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"OTP: {self.otp} - Active: {self.is_active}"
    
    class Meta:
        db_table = 'otps'

class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField()
    present = models.BooleanField(default=True)
    marked_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.student.name} - {self.date} - {'Present' if self.present else 'Absent'}"
    
    class Meta:
        db_table = 'attendance'
        unique_together = ['student', 'date']

class OTPValidation(models.Model):
    otp = models.CharField(max_length=10)
    validated_at = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField()
    
    def __str__(self):
        return f"OTP: {self.otp} - {'Success' if self.success else 'Failed'}"
    
    class Meta:
        db_table = 'otp_validations'

class AdminCredentials(models.Model):
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Admin: {self.username}"
    
    class Meta:
        db_table = 'admin_credentials'