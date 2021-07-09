from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.forms.utils import ErrorList
from django.http import HttpResponse
from .forms import LoginForm, SignUpForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    form = LoginForm(request.POST or None)
    msg = None

    if request.method == "POST":

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                try:
                    sessions = Session.objects.all()
                except Exception as ex:
                    msg = 'Some issue found with sessions'
                else:
                    if sessions.count() < 10:
                        login(request, user)
                        return redirect("/")
                    else:
                        msg = 'Already reached max users limit!'
            else:
                msg = 'Invalid credentials'
        else:
            msg = 'Error validating the form'

    return render(request, "accounts/login.html", {"form": form, "msg": msg})


def register_user(request):
    if request.user.is_authenticated:
        return redirect('home')
    msg = None
    success = False

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=raw_password)

            msg = 'User created - please <a href="/login">login</a>.'
            success = True
            if user is not None:
                try:
                    sessions = Session.objects.all()
                except Exception as ex:
                    msg = 'Some issue found with sessions'
                else:
                    if sessions.count() < 10:
                        login(request=request, user=user)
                        return redirect('userProfile')
                    else:
                        msg = 'User created, but already reached max logged in users limit!'

        else:
            msg = 'Form is not valid'
    else:
        form = SignUpForm()

    return render(request, "accounts/register.html", {"form": form, "msg": msg, "success": success})
