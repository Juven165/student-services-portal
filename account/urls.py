from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path(
        'login/',
        auth_views.LoginView.as_view(template_name='account/login.html'),
        name='login'
    ),

    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('send-email-activation/', views.send_email_activation, name='send_email_activation'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<uidb64>/<token>/', views.password_reset, name='reset_password'),
    path('dashboard/', views.dashboard, name='dashboard'),
]
