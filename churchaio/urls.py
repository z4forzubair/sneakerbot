from django.urls import path, re_path
from churchaio import views

urlpatterns = [

    # The home page
    # to revert these two
    path('landing/', views.index, name='home'),
    path('', views.LandingPageView.as_view(), name='landing_page_view'),

    # user
    path('user_profile/', views.user_profile, name='userProfile'),
    path('user_profile/update/', views.update_user_profile, name='updateUserProfile'),
    path('user_profile/change_picture/', views.update_profile_picture, name='updateProfilePicture'),

    # task
    path('tasks/', views.tasks, name='tasks'),
    path('tasks/create/', views.create_task, name='createTask'),
    path('tasks/<int:task_id>/update/', views.update_task, name='updateTask'),
    path('tasks/<int:task_id>/delete/', views.delete_task, name='deleteTask'),
    path('tasks/clear/', views.clear_tasks, name='clearTasks'),
    path('tasks/start_all/', views.start_all_tasks, name='startAllTasks'),
    path('tasks/<int:task_id>/start/', views.start_task, name='startTask'),


    # billing profile
    path('billing_profiles/', views.billing, name='billing'),
    path('billing_profiles/create/', views.create_billing, name='createBilling'),
    path('billing_profiles/<int:profile_id>/update/', views.update_billing, name='updateBilling'),
    path('billing_profiles/<int:profile_id>/delete/', views.delete_billing, name='deleteBilling'),
    path('billing_profiles/clear/', views.clear_billing, name='clearBilling'),
    path('billing_profiles/<int:profile_id>/updateFav/', views.update_favorite, name='updateFavorite'),

    # proxies
    path('proxies/', views.proxies, name='proxies'),
    path('proxies/create_list/', views.create_proxy_list, name='createProxyList'),
    path('proxies/create/', views.create_proxies, name='createProxies'),
    path('proxies/<int:proxy_id>/delete/', views.delete_proxy, name='deleteProxy'),
    path('proxies/set_list/', views.set_proxy_list, name='setProxyList'),

    # payment
    path('webhooks/stripe/', views.stripe_webhook, name='stripe_webhook'),
    path('success/<int:product_id>/', views.success_view, name='success'),
    path('cancel/<int:product_id>/', views.cancel_view, name='cancel'),
    path('create_checkout_session/<pk>/', views.CreateCheckoutSessionView.as_view(), name='create_checkout_session'),

    # Matches any html file
    # to change the following and its view to handle 404/500 responses
    # re_path(r'^.*\.*', views.pages, name='pages'),
]
