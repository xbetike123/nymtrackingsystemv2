from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout

def login_view(request):
    if request.method == 'POST':
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user:
            login(request, user)
            return redirect('admin_dashboard')
        return render(request, 'admin_views/login.html', {'error': 'Invalid credentials'})
    return render(request, 'admin_views/login.html')

def logout_view(request):
    logout(request)
    return redirect('login_view')
