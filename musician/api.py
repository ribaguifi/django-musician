import requests
import urllib.parse

from django.conf import settings
from django.http import Http404
from django.urls.exceptions import NoReverseMatch
from django.utils.translation import gettext_lazy as _

from .models import Domain, DatabaseService, MailService, SaasService, UserAccount


DOMAINS_PATH = 'domains/'
TOKEN_PATH = '/api-token-auth/'

API_PATHS = {
    # auth
    'token-auth': '/api-token-auth/',
    'my-account': 'accounts/',

    # services
    'database-list': 'databases/',
    'domain-list': 'domains/',
    'domain-detail': 'domains/{pk}/',
    'address-list': 'addresses/',
    'mailbox-list': 'mailboxes/',
    'mailinglist-list': 'lists/',
    'saas-list': 'saas/',

    # other
    'bill-list': 'bills/',
    'payment-source-list': 'payment-sources/',
}


class Orchestra(object):
    def __init__(self, *args, username=None, password=None, **kwargs):
        self.base_url = kwargs.pop('base_url', settings.API_BASE_URL)
        self.username = username
        self.session = requests.Session()
        self.auth_token = kwargs.pop("auth_token", None)

        if self.auth_token is None:
            self.auth_token = self.authenticate(self.username, password)

    def build_absolute_uri(self, path_name):
        path = API_PATHS.get(path_name, None)
        if path is None:
            raise NoReverseMatch(
                "Not found API path name '{}'".format(path_name))

        return urllib.parse.urljoin(self.base_url, path)

    def authenticate(self, username, password):
        url = self.build_absolute_uri('token-auth')
        response = self.session.post(
            url,
            data={"username": username, "password": password},
        )

        return response.json().get("token", None)

    def request(self, verb, resource=None, querystring=None, url=None, raise_exception=True):
        assert verb in ["HEAD", "GET", "POST", "PATCH", "PUT", "DELETE"]
        if resource is not None:
            url = self.build_absolute_uri(resource)
        elif url is None:
            raise AttributeError("Provide `resource` or `url` params")

        if querystring is not None:
            url = "{}?{}".format(url, querystring)

        verb = getattr(self.session, verb.lower())
        response = verb(url, headers={"Authorization": "Token {}".format(
            self.auth_token)}, allow_redirects=False)

        if raise_exception:
            response.raise_for_status()

        status = response.status_code
        output = response.json()

        return status, output

    def retrieve_service_list(self, service_name, querystring=None):
        pattern_name = '{}-list'.format(service_name)
        if pattern_name not in API_PATHS:
            raise ValueError("Unknown service {}".format(service_name))
        _, output = self.request("GET", pattern_name, querystring=querystring)
        return output

    def retrieve_profile(self):
        status, output = self.request("GET", 'my-account')
        if status >= 400:
            raise PermissionError("Cannot retrieve profile of an anonymous user.")
        return UserAccount.new_from_json(output[0])

    def retrieve_domain(self, pk):
        path = API_PATHS.get('domain-detail').format_map({'pk': pk})

        url = urllib.parse.urljoin(self.base_url, path)
        status, domain_json = self.request("GET", url=url, raise_exception=False)
        if status == 404:
            raise Http404(_("No domain found matching the query"))
        return Domain.new_from_json(domain_json)

    def retrieve_domain_list(self):
        output = self.retrieve_service_list(Domain.api_name)
        domains = []
        for domain_json in output:
            # filter querystring
            querystring = "domain={}".format(domain_json['id'])

            # retrieve services associated to a domain
            domain_json['mails'] = self.retrieve_service_list(
                MailService.api_name, querystring)
            # TODO(@slamora): databases and sass are not related to a domain, so cannot be filtered
            # domain_json['databases'] = self.retrieve_service_list(DatabaseService.api_name, querystring)
            # domain_json['saas'] = self.retrieve_service_list(SaasService.api_name, querystring)

            # TODO(@slamora): update when backend provides resource disk usage data
            domain_json['usage'] = {
                'usage': 300,
                'total': 650,
                'unit': 'MB',
                'percent': 50,
            }

            # append to list a Domain object
            domains.append(Domain.new_from_json(domain_json))

        return domains

    def verify_credentials(self):
        """
        Returns:
          A user profile info if the
          credentials are valid, None otherwise.
        """
        status, output = self.request("GET", 'my-account', raise_exception=False)

        if status < 400:
            return output

        return None
