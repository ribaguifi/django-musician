from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic.base import ContextMixin

from . import get_version
from .auth import SESSION_KEY_TOKEN


class CustomContextMixin(ContextMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # TODO generate menu items
        context.update({
            'version': get_version(),
        })

        return context


class UserTokenRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        """Check that the user has an authorized token."""
        token = self.request.session.get(SESSION_KEY_TOKEN, None)
        if token is None:
            return False

        # initialize orchestra api orm
        self.orchestra = api.Orchestra(auth_token=token)

        # verify if the token is valid
        if self.orchestra.verify_credentials() is None:
            return False

        return True
