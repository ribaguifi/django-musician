
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
    path('domains/<int:pk>/', views.DomainDetailView.as_view(), name='domain-detail'),
    path('billing/', views.BillingView.as_view(), name='billing'),
    path('bills/<int:pk>/download/', views.BillDownloadView.as_view(), name='bill-download'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('address/', views.MailView.as_view(), name='address-list'),
    path('address/new/', views.MailCreateView.as_view(), name='address-create'),
    path('address/<int:pk>/', views.MailUpdateView.as_view(), name='address-update'),
    path('mailboxes/', views.MailboxesView.as_view(), name='mailbox-list'),
    path('mailing-lists/', views.MailingListsView.as_view(), name='mailing-lists'),
    path('databases/', views.DatabasesView.as_view(), name='database-list'),
    path('saas/', views.SaasView.as_view(), name='saas-list'),
]
