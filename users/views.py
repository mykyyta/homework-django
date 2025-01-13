from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.contrib.auth.models import User, Group
from django.shortcuts import render, redirect
from .forms import RegisterForm, LoginForm

def user_page(request):
    return redirect('index_page')

def specific_user(request, user_id):
    current_client = User.objects.get(pk=user_id)
    return render(request, 'client_account.html', {'client':current_client})

def login_page(request):
    if request.method == "POST":
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user = authenticate(
                request,
                username=login_form.cleaned_data['username'],
                password=login_form.cleaned_data['password']
                )
            if user is not None:
                login(request, user)
                return redirect('index_page')
        messages.error(request, "Invalid username or password")
        return redirect('login_page', )
    else:
        form = LoginForm()
        return render(request, 'login.html', {'form': form})


def logout_page(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect('index_page')
    return HttpResponse("You are not logged in")

def register(request, user_type):
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()
        group_name = 'trainer' if user_type == 'trainer' else 'client'
        user.groups.add(Group.objects.get(name=group_name))
        return redirect('login_page')

    return render(request, 'register.html', {'form': form, 'user_type': user_type})

def index_page(request):
    return render(request, 'index.html')