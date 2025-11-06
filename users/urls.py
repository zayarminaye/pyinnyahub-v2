"""
URLs for Users app.
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # Web Views
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),

    # API Views
    path('api/auth/register/', views.RegisterAPIView.as_view(), name='api_register'),
    path('api/auth/login/', views.LoginAPIView.as_view(), name='api_login'),
    path('api/auth/logout/', views.LogoutAPIView.as_view(), name='api_logout'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='api_token_refresh'),
    path('api/auth/profile/', views.UserProfileAPIView.as_view(), name='api_profile'),
    path('api/auth/change-password/', views.ChangePasswordAPIView.as_view(), name='api_change_password'),
]
