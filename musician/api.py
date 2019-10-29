import urllib.parse

from django.conf import settings
from django.urls.exceptions import NoReverseMatch

DOMAINS_PATH = 'domains/'
TOKEN_PATH = '/api-token-auth/'

API_PATHS = {
    # auth
    'token-auth': '/api-token-auth/',

    # services
    'domain-list': 'domains/',
    # ... TODO (@slamora) complete list of backend URLs
}


def build_absolute_uri(path_name):
    path = API_PATHS.get(path_name, None)
    if path is None:
        raise NoReverseMatch("Not found API path name '{}'".format(path_name))

    return urllib.parse.urljoin(settings.API_BASE_URL, path)
