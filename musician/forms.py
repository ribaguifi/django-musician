
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError

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


class MailForm(forms.Form):
    name = forms.CharField()
    domain = forms.ChoiceField()
    mailboxes = forms.MultipleChoiceField(required=False)
    forward = forms.EmailField(required=False)

    def __init__(self, *args, **kwargs):
        instance = kwargs.pop('instance', None)
        if instance is not None:
            kwargs['initial'] = instance.deserialize()

        domains = kwargs.pop('domains')
        mailboxes = kwargs.pop('mailboxes')

        super().__init__(*args, **kwargs)
        self.fields['domain'].choices = [(d.url, d.name) for d in domains]
        self.fields['mailboxes'].choices = [(m.url, m.name) for m in mailboxes]

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('mailboxes') and not cleaned_data.get('forward'):
            raise ValidationError("A mailbox or forward address should be provided.")
        return cleaned_data

    def serialize(self):
        assert hasattr(self, 'cleaned_data')
        serialized_data = {
            "name": self.cleaned_data["name"],
            "domain": {"url": self.cleaned_data["domain"]},
            "mailboxes": [{"url": mbox} for mbox in self.cleaned_data["mailboxes"]],
            "forward": self.cleaned_data["forward"],
        }
        return serialized_data
