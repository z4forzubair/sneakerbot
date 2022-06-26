# Create your views here.
import datetime

from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.views import LogoutView
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect

from authentication.views_dir.login import login_helper
from churchaio.alerts import LOGIN_ALERTS, GENERAL_ALERTS
from .forms import LoginForm


class MyLogoutView(LogoutView):

    # modifying the method inside LogoutView
    def dispatch(self, request, *args, **kwargs):
        expired = request.session.get("expired")
        auth_logout(request)
        request.session["expired"] = expired
        next_page = self.get_next_page()
        if next_page:
            # Redirect to this page until the session has been cleared.
            return HttpResponseRedirect(next_page)
        return super().dispatch(request, *args, **kwargs)


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = LoginForm(request.POST or None)

    success = None
    msg = None
    expired = request.session.get('expired')
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

                        login_allow, data = login_helper(request=request, user=user)
                        if login_allow:
                            login(request, user)
                            if data is not None:
                                request.session['p_usr_login'] = data
                            return redirect(redirect_to)
                        else:
                            msg = data
                else:
                    success = False
                    msg = LOGIN_ALERTS.get("invalid")
            else:
                success = False
                msg = LOGIN_ALERTS.get("form_error")

    context = {}
    if expired:
        request.session["expired"] = None
        msg = LOGIN_ALERTS.get("expired")
        context["STRIPE_PUBLIC_KEY"] = settings.STRIPE_PUBLIC_KEY
        context["product_id"] = 2
    else:
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

    context["form"] = form
    context["banner_msg"] = msg
    context["success"] = success

    return render(request, "accounts/login.html", context=context)
