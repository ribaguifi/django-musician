import requests
import urllib.parse

from django.conf import settings
from django.urls.exceptions import NoReverseMatch

DOMAINS_PATH = 'domains/'
TOKEN_PATH = '/api-token-auth/'

API_PATHS = {
    # auth
    'token-auth': '/api-token-auth/',
    'my-account': 'accounts/',

    # services
    'domain-list': 'domains/',
    # ... TODO (@slamora) complete list of backend URLs
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

    def request(self, verb, resource, raise_exception=True):
        assert verb in ["HEAD", "GET", "POST", "PATCH", "PUT", "DELETE"]
        url = self.build_absolute_uri(resource)

        verb = getattr(self.session, verb.lower())
        response = verb(url, headers={"Authorization": "Token {}".format(
            self.auth_token)}, allow_redirects=False)

        if raise_exception:
            response.raise_for_status()

        status = response.status_code
        output = response.json()

        return status, output

    def retrieve_domains(self):
        status, output = self.request("GET", 'domain-list')
        return output

    def retreve_profile(self):
        _, output = self.request("GET", 'my-account')
        return output

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
