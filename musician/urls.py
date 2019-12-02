
"""
URL routes definition.

Describe the paths where the views are accesible.
"""
from django.urls import path

from . import views


app_name = 'musician'

urlpatterns = [
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('auth/logout/', views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('mails/', views.MailView.as_view(), name='mails'),
    path('mailing-lists/', views.MailingListsView.as_view(), name='mailing-lists'),
    path('databases/', views.DatabasesView.as_view(), name='databases'),
    path('software-as-a-service/', views.SaasView.as_view(), name='saas'),
]
