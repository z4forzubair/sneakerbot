from django.urls import path, re_path
from churchaio import views

urlpatterns = [

    # The home page
    path('', views.index, name='home'),

    # user
    path('user_profile/', views.userProfile, name='userProfile'),
    path('user_profile/update/', views.updateUserProfile, name='updateUserProfile'),
    path('user_profile/change_picture/', views.updateProfilePicture, name='updateProfilePicture'),

    # task
    path('tasks/', views.tasks, name='tasks'),
    path('tasks/create/', views.createTask, name='createTask'),
    path('tasks/<int:task_id>/update/', views.updateTask, name='updateTask'),
    path('tasks/<int:task_id>/delete/', views.deleteTask, name='deleteTask'),
    path('tasks/clear/', views.clearTasks, name='clearTasks'),
    path('tasks/start_all/', views.startAllTasks, name='startAllTasks'),
    path('tasks/<int:task_id>/start/', views.startTask, name='startTask'),


    # billing profile
    path('billing_profiles/', views.billing, name='billing'),
    path('billing_profiles/create/', views.createBilling, name='createBilling'),
    path('billing_profiles/<int:profile_id>/update/', views.updateBilling, name='updateBilling'),
    path('billing_profiles/<int:profile_id>/delete/', views.deleteBilling, name='deleteBilling'),
    path('billing_profiles/clear/', views.clearBilling, name='clearBilling'),
    path('billing_profiles/<int:profile_id>/updateFav/', views.updateFavorite, name='updateFavorite'),

    # Matches any html file
    # to change the following and its view to handle 404/500 responses
    re_path(r'^.*\.*', views.pages, name='pages'),
]
