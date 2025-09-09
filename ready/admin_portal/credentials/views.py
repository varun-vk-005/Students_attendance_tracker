from django.shortcuts import render, redirect
from django.contrib import messages
from .mongodb_utils import get_admin_credentials, update_admin_credentials, validate_admin

def login_view(request):
    if request.method == "POST":
        if validate_admin(request.POST['username'], request.POST['password']):
            request.session['admin'] = True
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid credentials")
    return render(request, 'login.html')

def dashboard_view(request):
    if not request.session.get('admin'):
        return redirect('login')
    return render(request, 'dashboard.html', {"admin": get_admin_credentials()})

def update_view(request):
    if request.method == "POST":
        if update_admin_credentials(request.POST['username'], request.POST['password']):
            messages.success(request, "Admin credentials updated.")
        else:
            messages.error(request, "Update failed.")
    return redirect('dashboard')
