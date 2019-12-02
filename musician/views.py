
from django.views.generic.detail import DetailView
from itertools import groupby

from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.http import is_safe_url
from django.views.generic.base import RedirectView, TemplateView
from django.views.generic.edit import FormView
from django.views.generic.list import ListView

from . import api, get_version
from .auth import login as auth_login
from .auth import logout as auth_logout
from .forms import LoginForm
from .mixins import (CustomContextMixin,
                     ExtendedPaginationMixin, UserTokenRequiredMixin)
from .models import DatabaseService, MailinglistService, MailService, UserAccount, PaymentSource


class DashboardView(CustomContextMixin, UserTokenRequiredMixin, TemplateView):
    template_name = "musician/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # TODO retrieve all data needed from orchestra
        raw_domains = self.orchestra.retrieve_service_list('domain')

        context.update({
            'domains': raw_domains
        })

        return context


class ProfileView(CustomContextMixin, UserTokenRequiredMixin, TemplateView):
    template_name = "musician/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        json_data = self.orchestra.retreve_profile()
        try:
            pay_source = self.orchestra.retrieve_service_list(
                PaymentSource.api_name)[0]
        except IndexError:
            pay_source = {}
        context.update({
            'profile': UserAccount.new_from_json(json_data[0]),
            'payment': PaymentSource.new_from_json(pay_source)
        })

        return context


class ServiceListView(CustomContextMixin, ExtendedPaginationMixin, UserTokenRequiredMixin, ListView):
    """Base list view to all services"""
    service_class = None
    template_name = "musician/service_list.html"  # TODO move to ServiceListView

    def get_queryset(self):
        if self.service_class is None or self.service_class.api_name is None:
            raise ImproperlyConfigured(
                "ServiceListView requires a definiton of 'service'")

        json_qs = self.orchestra.retrieve_service_list(
            self.service_class.api_name)
        return [self.service_class.new_from_json(data) for data in json_qs]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'service': self.service_class,
        })
        return context


class MailView(ServiceListView):
    service_class = MailService
    template_name = "musician/mail.html"

    def get_queryset(self):
        def retrieve_mailbox(value):
            mailboxes = value.get('mailboxes')

            if len(mailboxes) == 0:
                return ''

            return mailboxes[0]['id']

        # group addresses with the same mailbox
        raw_data = self.orchestra.retrieve_service_list(
            self.service_class.api_name)
        addresses = []
        for key, group in groupby(raw_data, retrieve_mailbox):
            aliases = []
            data = {}
            for thing in group:
                aliases.append(thing.pop('name'))
                data = thing

            data['names'] = aliases
            addresses.append(self.service_class.new_from_json(data))

        return addresses


class MailingListsView(ServiceListView):
    service_class = MailinglistService


class DatabasesView(ServiceListView):
    template_name = "musician/databases.html"
    service_class = DatabaseService


class SaasView(CustomContextMixin, UserTokenRequiredMixin, TemplateView):
    template_name = "musician/saas.html"


class LoginView(FormView):
    template_name = 'auth/login.html'
    form_class = LoginForm
    success_url = reverse_lazy('musician:dashboard')
    redirect_field_name = 'next'
    extra_context = {'version': get_version()}

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        """Security check complete. Log the user in."""
        auth_login(self.request, form.username, form.token)
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        url = self.get_redirect_url()
        return url or self.success_url

    def get_redirect_url(self):
        """Return the user-originating redirect URL if it's safe."""
        redirect_to = self.request.POST.get(
            self.redirect_field_name,
            self.request.GET.get(self.redirect_field_name, '')
        )
        url_is_safe = is_safe_url(
            url=redirect_to,
            allowed_hosts={self.request.get_host()},
            require_https=self.request.is_secure(),
        )
        return redirect_to if url_is_safe else ''

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            self.redirect_field_name: self.get_redirect_url(),
            **(self.extra_context or {})
        })
        return context


class LogoutView(RedirectView):
    """
    Log out the user.
    """
    permanent = False
    pattern_name = 'musician:login'

    def get_redirect_url(self, *args, **kwargs):
        """
        Logs out the user.
        """
        auth_logout(self.request)
        return super().get_redirect_url(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Logout may be done via POST."""
        return self.get(request, *args, **kwargs)
