from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.contrib.auth.models import User, Group
from django.shortcuts import render, redirect
from .forms import RegisterForm

def user_page(request):
    return HttpResponse("Hello, world. You're at the polls index.")

def specific_user(request, user_id):
    return HttpResponse(f"Hello, {user_id}. You're at the polls index.")

def login_page(request):
    if request.method == "POST":
        username = request.POST.get('username', 'Guest')
        password = request.POST.get('password')

        if not username or not password:
            return HttpResponse("Missing username or password", status=400)

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index_page')
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password.'})
    else:
        return render(request, 'login.html')


def logout_page(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect('index_page')
    return HttpResponse("You are not logged in")

def register_page(request, user_type):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password = form.cleaned_data['password'],
                first_name = form.cleaned_data['first_name'],
                last_name = form.cleaned_data['last_name'],
                email = form.cleaned_data['email'],
                )
            group_name = 'trainer' if user_type == 'trainer' else 'client'
            user.groups.add(Group.objects.get(name=group_name))
            return redirect('login_page')
        else:
            return render(request, 'register.html', {'form': form})
    else:
        form = RegisterForm()
        return render(request, 'register.html', {'form': form, 'user_type': user_type})

def index_page(request):
    return render(request, 'index.html')