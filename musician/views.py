from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic.base import TemplateView

from .mixins import CustomContextMixin


class DashboardView(CustomContextMixin, TemplateView):  ## TODO LoginRequiredMixin
    template_name = "musician/dashboard.html"
