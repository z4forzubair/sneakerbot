from django.urls import path, re_path
from churchaio import views


urlpatterns = [

    # The home page
    path('', views.index, name='home'),
    path('tasks', views.tasks, name= 'tasks'),

    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages'),
]
