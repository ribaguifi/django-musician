from itertools import groupby

from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.http import is_safe_url
from django.utils.translation import gettext_lazy as _
from django.views.generic.base import RedirectView, TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from django.views.generic.list import ListView

from . import api, get_version
from .auth import login as auth_login
from .auth import logout as auth_logout
from .forms import LoginForm
from .mixins import (CustomContextMixin, ExtendedPaginationMixin,
                     UserTokenRequiredMixin)
from .models import (DatabaseService, MailinglistService, MailService,
                     PaymentSource, SaasService, UserAccount)
from .settings import ALLOWED_RESOURCES


class DashboardView(CustomContextMixin, UserTokenRequiredMixin, TemplateView):
    template_name = "musician/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        domains = self.orchestra.retrieve_domain_list()

        # TODO(@slamora) update when backend provides resource usage data
        resource_usage = {
            'disk': {
                'verbose_name': _('Disk usage'),
                'usage': 534,
                'total': 1024,
                'unit': 'MB',
                'percent': 50,
            },
            'traffic': {
                'verbose_name': _('Traffic'),
                'usage': 300,
                'total': 2048,
                'unit': 'MB/month',
                'percent': 25,
            },
            'mailbox': {
                'verbose_name': _('Mailbox usage'),
                'usage': 1,
                'total': 2,
                'unit': 'accounts',
                'percent': 50,
            },
        }

        # TODO(@slamora) update when backend supports notifications
        notifications = []

        # show resource usage based on plan definition
        # TODO(@slamora): validate concept of limits with Pangea
        profile_type = context['profile'].type
        for domain in domains:
            address_left = ALLOWED_RESOURCES[profile_type]['mailbox'] - len(domain.mails)
            alert = None
            if address_left == 1:
                alert = 'warning'
            elif address_left < 1:
                alert = 'danger'

            domain.address_left = {
                'count': address_left,
                'alert': alert,
            }

        context.update({
            'domains': domains,
            'resource_usage': resource_usage,
            'notifications': notifications,
        })

        return context


class BillingView(CustomContextMixin, ExtendedPaginationMixin, UserTokenRequiredMixin, ListView):
    template_name = "musician/billing.html"

    def get_queryset(self):
        # TODO (@slamora) retrieve user bills
        from django.utils import timezone
        return [
            {
                'number': 24,
                'date': timezone.now(),
                'type': 'subscription',
                'total_amount': '25,00 €',
                'status': 'paid',
                'pdf_url': 'https://example.org/bill.pdf'
            },
        ]


class ProfileView(CustomContextMixin, UserTokenRequiredMixin, TemplateView):
    template_name = "musician/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            pay_source = self.orchestra.retrieve_service_list(
                PaymentSource.api_name)[0]
        except IndexError:
            pay_source = {}
        context.update({
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

            # forwarded address should not grouped
            if len(mailboxes) == 0:
                return value.get('name')

            return mailboxes[0]['id']

        # retrieve mails applying filters (if any)
        queryfilter = self.get_queryfilter()
        raw_data = self.orchestra.retrieve_service_list(
            self.service_class.api_name,
            querystring=queryfilter,
        )

        # group addresses with the same mailbox
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

    def get_queryfilter(self):
        """Retrieve query params (if any) to filter queryset"""
        domain_id = self.request.GET.get('domain')
        if domain_id:
            return "domain={}".format(domain_id)

        return ''

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        domain_id = self.request.GET.get('domain')
        if domain_id:
            context.update({
                'active_domain': self.orchestra.retrieve_domain(domain_id)
            })
        return context


class MailingListsView(ServiceListView):
    service_class = MailinglistService
    template_name = "musician/mailinglists.html"


class DatabasesView(ServiceListView):
    template_name = "musician/databases.html"
    service_class = DatabaseService


class SaasView(ServiceListView):
    service_class = SaasService
    template_name = "musician/saas.html"


class DomainDetailView(CustomContextMixin, UserTokenRequiredMixin, DetailView):
    template_name = "musician/domain_detail.html"

    def get_queryset(self):
        # Return an empty list to avoid a request to retrieve all the
        # user domains. We will get a 404 if the domain doesn't exists
        # while invoking `get_object`
        return []

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()

        pk = self.kwargs.get(self.pk_url_kwarg)
        domain = self.orchestra.retrieve_domain(pk)

        return domain


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
