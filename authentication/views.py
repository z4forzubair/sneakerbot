# Create your views here.
import datetime

from django.conf import settings
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

from churchaio.alerts import LOGIN_ALERTS, GENERAL_ALERTS
from .forms import LoginForm, SignUpForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = LoginForm(request.POST or None)

    success = None
    msg = None
    expired = None
    if request.method == "POST":

        if request.session.get('_new_sub') is None:
            if form.is_valid():
                username = form.cleaned_data.get("username")
                password = form.cleaned_data.get("password")
                user = authenticate(username=username, password=password)
                if user is not None:
                    try:
                        account = user.account
                        expired = True if account.expiry_date < datetime.date.today() else False
                    except Exception:
                        msg = GENERAL_ALERTS.get("unknown_error")
                    if expired == False:
                        redirect_to = "userProfile" if user.last_login is None else "home"
                        login(request, user)
                        return redirect(redirect_to)
                    elif expired == True:
                        msg = LOGIN_ALERTS.get("expired")
                else:
                    success = False
                    msg = LOGIN_ALERTS.get("invalid")
            else:
                success = False
                msg = LOGIN_ALERTS.get("form_error")

    new_user = request.session.get('_new_user')
    if new_user == True:
        request.session['_new_user'] = None
        success = True
        msg = LOGIN_ALERTS.get("stripe_success")
    elif new_user == False:
        request.session['_new_user'] = None
        success = False
        msg = LOGIN_ALERTS.get("stripe_fail")

    new_sub = request.session.get('_new_sub')
    if new_sub == True:
        request.session['_new_sub'] = None
        success = True
        msg = LOGIN_ALERTS.get("stripe_subscribe")
    elif new_sub == False:
        request.session['_new_sub'] = None
        success = False
        msg = LOGIN_ALERTS.get("stripe_fail")

    context = {
        "form": form,
        "banner_msg": msg,
        "success": success
    }

    if expired:
        context["STRIPE_PUBLIC_KEY"] = settings.STRIPE_PUBLIC_KEY
        context["product_id"] = 2

    return render(request, "accounts/login.html", context=context)


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
                login(request=request, user=user)
                return redirect('userProfile')

        else:
            msg = 'Form is not valid'
    else:
        form = SignUpForm()

    return render(request, "accounts/register.html", {"form": form, "msg": msg, "success": success})
