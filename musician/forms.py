import urllib.parse

import requests
from django.contrib.auth.forms import AuthenticationForm

from . import api


def authenticate(username, password):
    url = api.build_absolute_uri('token-auth')
    r = requests.post(
        url,
        data={"username": username, "password": password},
    )

    token = r.json().get("token", None)
    return token


class LoginForm(AuthenticationForm):

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username is not None and password:
            self.token = authenticate(username, password)
            if self.token is None:
                raise self.get_invalid_login_error()
            else:
                return self.token

        return self.cleaned_data
