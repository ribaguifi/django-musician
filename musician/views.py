from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils import translation
from django.utils.http import is_safe_url
from django.utils.translation import gettext_lazy as _
from django.views import View
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
from .models import (Bill, DatabaseService, MailinglistService, MailService,
                     PaymentSource, SaasService, UserAccount)
from .settings import ALLOWED_RESOURCES
from .utils import get_bootstraped_percent


class DashboardView(CustomContextMixin, UserTokenRequiredMixin, TemplateView):
    template_name = "musician/dashboard.html"
    extra_context = {
        # Translators: This message appears on the page title
        'title': _('Dashboard'),
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        domains = self.orchestra.retrieve_domain_list()

        # TODO(@slamora) update when backend supports notifications
        notifications = []

        # show resource usage based on plan definition
        profile_type = context['profile'].type
        total_mailboxes = 0
        for domain in domains:
            total_mailboxes += len(domain.mails)
            addresses_left = ALLOWED_RESOURCES[profile_type]['mailbox'] - len(domain.mails)
            alert_level = None
            if addresses_left == 1:
                alert_level = 'warning'
            elif addresses_left < 1:
                alert_level = 'danger'

            domain.addresses_left = {
                'count': addresses_left,
                'alert_level': alert_level,
            }

        # TODO(@slamora) update when backend provides resource usage data
        resource_usage = {
            'disk': {
                'verbose_name': _('Disk usage'),
                'data': {
                    # 'usage': 534,
                    # 'total': 1024,
                    # 'unit': 'MB',
                    # 'percent': 50,
                },
            },
            'traffic': {
                'verbose_name': _('Traffic'),
                'data': {
                    # 'usage': 300,
                    # 'total': 2048,
                    # 'unit': 'MB/month',
                    # 'percent': 25,
                },
            },
            'mailbox': {
                'verbose_name': _('Mailbox usage'),
                'data': {
                    'usage': total_mailboxes,
                    'total': ALLOWED_RESOURCES[profile_type]['mailbox'],
                    'unit': 'accounts',
                    'percent': get_bootstraped_percent(total_mailboxes, ALLOWED_RESOURCES[profile_type]['mailbox']),
                },
            },
        }

        context.update({
            'domains': domains,
            'resource_usage': resource_usage,
            'notifications': notifications,
        })

        return context


class ProfileView(CustomContextMixin, UserTokenRequiredMixin, TemplateView):
    template_name = "musician/profile.html"
    extra_context = {
        # Translators: This message appears on the page title
        'title': _('User profile'),
    }

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
    template_name = "musician/service_list.html"

    def get_queryset(self):
        if self.service_class is None or self.service_class.api_name is None:
            raise ImproperlyConfigured(
                "ServiceListView requires a definiton of 'service'")

        queryfilter = self.get_queryfilter()
        json_qs = self.orchestra.retrieve_service_list(
            self.service_class.api_name,
            querystring=queryfilter,
        )
        return [self.service_class.new_from_json(data) for data in json_qs]

    def get_queryfilter(self):
        """Does nothing by default. Should be implemented on subclasses"""
        return ''

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'service': self.service_class,
        })
        return context


class BillingView(ServiceListView):
    service_class = Bill
    template_name = "musician/billing.html"
    extra_context = {
        # Translators: This message appears on the page title
        'title': _('Billing'),
    }


class BillDownloadView(CustomContextMixin, UserTokenRequiredMixin, View):
    extra_context = {
        # Translators: This message appears on the page title
        'title': _('Download bill'),
    }

    def get(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        bill = self.orchestra.retrieve_bill_document(pk)

        return HttpResponse(bill)


class MailView(ServiceListView):
    service_class = MailService
    template_name = "musician/mail.html"
    extra_context = {
        # Translators: This message appears on the page title
        'title': _('Mail addresses'),
    }

    def get_queryset(self):
        # retrieve mails applying filters (if any)
        queryfilter = self.get_queryfilter()
        addresses = self.orchestra.retrieve_mail_address_list(
            querystring=queryfilter
        )
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
    extra_context = {
        # Translators: This message appears on the page title
        'title': _('Mailing lists'),
    }


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        domain_id = self.request.GET.get('domain')
        if domain_id:
            context.update({
                'active_domain': self.orchestra.retrieve_domain(domain_id)
            })
        return context

    def get_queryfilter(self):
        """Retrieve query params (if any) to filter queryset"""
        # TODO(@slamora): this is not working because backend API
        #   doesn't support filtering by domain
        domain_id = self.request.GET.get('domain')
        if domain_id:
            return "domain={}".format(domain_id)

        return ''


class DatabasesView(ServiceListView):
    template_name = "musician/databases.html"
    service_class = DatabaseService
    extra_context = {
        # Translators: This message appears on the page title
        'title': _('Databases'),
    }


class SaasView(ServiceListView):
    service_class = SaasService
    template_name = "musician/saas.html"
    extra_context = {
        # Translators: This message appears on the page title
        'title': _('Software as a Service'),
    }


class DomainDetailView(CustomContextMixin, UserTokenRequiredMixin, DetailView):
    template_name = "musician/domain_detail.html"
    extra_context = {
        # Translators: This message appears on the page title
        'title': _('Domain details'),
    }

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
    extra_context = {
        # Translators: This message appears on the page title
        'title': _('Login'),
        'version': get_version(),
    }

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        """Security check complete. Log the user in."""
        auth_login(self.request, form.username, form.token)

        # set user language as active language
        user_language = form.user.language
        translation.activate(user_language)

        response = HttpResponseRedirect(self.get_success_url())
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, user_language)

        return response

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
