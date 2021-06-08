from django.urls import path, re_path
from churchaio import views

urlpatterns = [

    # The home page
    path('', views.index, name='home'),
    path('tasks', views.tasks, name='tasks'),
    path('tasks/create', views.createTask, name='createTask'),
    path('tasks/<int:task_id>/update', views.updateTask, name='updateTask'),
    path('tasks/<int:task_id>/delete', views.deleteTask, name='deleteTask'),
    path('tasks/clear', views.clearTasks, name='clearTasks'),

    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages'),
]
