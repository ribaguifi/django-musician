from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView

from . import api, get_version
from .forms import LoginForm
from .mixins import CustomContextMixin


class DashboardView(CustomContextMixin, TemplateView):  ## TODO LoginRequiredMixin
    template_name = "musician/dashboard.html"


class LoginView(FormView):
    template_name = 'auth/login.html'
    form_class = LoginForm
    success_url = reverse_lazy('musician:dashboard')
    extra_context = {'version': get_version()}
