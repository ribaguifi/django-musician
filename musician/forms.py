
from django.contrib.auth.forms import AuthenticationForm

from . import api

class LoginForm(AuthenticationForm):

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username is not None and password:
            orchestra = api.Orchestra(username=username, password=password)

            if orchestra.auth_token is None:
                raise self.get_invalid_login_error()
            else:
                self.username = username
                self.token = orchestra.auth_token
                self.user = orchestra.retrieve_profile()

        return self.cleaned_data
