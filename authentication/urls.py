from django.urls import path

from .views import login_view, MyLogoutView

urlpatterns = [
    path('login/', login_view, name="login"),
    path("logout/", MyLogoutView.as_view(), name="logout")
]
