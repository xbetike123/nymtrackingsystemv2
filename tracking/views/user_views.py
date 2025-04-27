from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Login view
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('admin_dashboard')
        else:
            return render(request, 'admin_views/login.html', {'error': 'Invalid credentials'})
    return render(request, 'admin_views/login.html')

# Logout view
def logout_view(request):
    logout(request)
    return redirect('login_view')

# Add new user (admin_views panel)
@login_required
def add_user_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user_level = request.POST.get('user_level')  # e.g. "superadmin" or "staff"

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        else:
            user = User.objects.create_user(username=username, password=password)
            user.is_staff = True
            user.is_superuser = (user_level == 'superadmin')
            user.save()
            messages.success(request, "User created successfully.")
            return redirect('add_user')

    return render(request, 'admin_views/add_user.html')
