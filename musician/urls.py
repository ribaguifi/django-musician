
"""
URL routes definition.

Describe the paths where the views are accesible.
"""
from django.contrib.auth import views as auth_views
from django.urls import path

from . import views


app_name = 'musician'

urlpatterns = [
    path('auth/login/', auth_views.LoginView.as_view(template_name='auth/login.html',
                                                     extra_context={'version': '0.1'}), name='login'),
    # path('auth/logout/', views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
]
