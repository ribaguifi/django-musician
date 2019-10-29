
"""
URL routes definition.

Describe the paths where the views are accesible.
"""
from django.urls import path

from . import views


app_name = 'musician'

urlpatterns = [
    path('auth/login/', views.LoginView.as_view(), name='login'),
    # path('auth/logout/', views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
]
