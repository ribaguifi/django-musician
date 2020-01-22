import ast
import logging

from django.utils.dateparse import parse_datetime
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from . import settings as musician_settings


logger = logging.getLogger(__name__)


class OrchestraModel:
    """ Base class from which all orchestra models will inherit. """
    api_name = None
    verbose_name = None
    fields = ()
    id = None

    def __init__(self, **kwargs):
        if self.verbose_name is None:
            self.verbose_name = self.api_name

        for (param, default) in self.param_defaults.items():
            setattr(self, param, kwargs.get(param, default))


    @classmethod
    def new_from_json(cls, data, **kwargs):
        """ Create a new instance based on a JSON dict. Any kwargs should be
        supplied by the inherited, calling class.
        Args:
            data: A JSON dict, as converted from the JSON in the orchestra API.
        """

        json_data = data.copy()
        if kwargs:
            for key, val in kwargs.items():
                json_data[key] = val

        c = cls(**json_data)
        c._json = data

        return c

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self)

    def __str__(self):
        return '%s object (%s)' % (self.__class__.__name__, self.id)


class Bill(OrchestraModel):
    api_name = 'bill'
    param_defaults = {
        "id": None,
        "number": "1",
        "type": "INVOICE",
        "total": 0.0,
        "is_sent": False,
        "created_on": "",
        "due_on": "",
        "comments": "",
    }


class BillingContact(OrchestraModel):
    param_defaults = {
        'name': None,
        'address': None,
        'city': None,
        'zipcode': None,
        'country': None,
        'vat': None,
    }


class PaymentSource(OrchestraModel):
    api_name = 'payment-source'
    param_defaults = {
        "method": None,
        "data": [],
        "is_active": False,
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # payment details are passed as a plain string
        # try to convert to a python structure
        try:
            self.data = ast.literal_eval(self.data)
        except (ValueError, SyntaxError) as e:
            logger.error(e)


class UserAccount(OrchestraModel):
    api_name = 'accounts'
    param_defaults = {
        'username': None,
        'type': None,
        'language': None,
        'short_name': None,
        'full_name': None,
        'billing': {},
        'last_login': None,
    }

    @classmethod
    def new_from_json(cls, data, **kwargs):
        billing = None
        last_login = None

        if 'billcontact' in data:
            billing = BillingContact.new_from_json(data['billcontact'])

        if 'last_login' in data:
            last_login = parse_datetime(data['last_login'])
        return super().new_from_json(data=data, billing=billing, last_login=last_login)


class DatabaseUser(OrchestraModel):
    api_name = 'databaseusers'
    fields = ('username',)
    param_defaults = {
        'username': None,
    }


class DatabaseService(OrchestraModel):
    api_name = 'database'
    verbose_name = _('Databases')
    fields = ('name', 'type', 'users')
    param_defaults = {
        "id": None,
        "name": None,
        "type": None,
        "users": None,
        "usage": {},
    }

    @classmethod
    def new_from_json(cls, data, **kwargs):
        users = None
        if 'users' in data:
            users = [DatabaseUser.new_from_json(user_data) for user_data in data['users']]

        # TODO(@slamora) retrieve database usage
        usage = {
            'usage': 250,
            'total': 500,
            'unit': 'MB',
            'percent': 50,
        }

        return super().new_from_json(data=data, users=users, usage=usage)


class Domain(OrchestraModel):
    api_name = 'domain'
    param_defaults = {
        "id": None,
        "name": None,
        "records": [],
        "mails": [],
        "usage": {},
        "websites": [],
    }

    @classmethod
    def new_from_json(cls, data, **kwargs):
        records = cls.param_defaults.get("records")
        if 'records' in data:
            records = [DomainRecord.new_from_json(record_data) for record_data in data['records']]

        return super().new_from_json(data=data, records=records)

    def __str__(self):
        return self.name


class DomainRecord(OrchestraModel):
    param_defaults = {
        "type": None,
        "value": None,
    }
    def __str__(self):
        return '<%s: %s>' % (self.type, self.value)


class MailService(OrchestraModel):
    api_name = 'address'
    verbose_name = _('Mail addresses')
    description = _('Litle description of what to be expected in this section to aid the user. Even a link to more help if there is one available.')
    fields = ('mail_address', 'aliases', 'type', 'type_detail')
    param_defaults = {}

    FORWARD = 'forward'
    MAILBOX = 'mailbox'

    def __init__(self, **kwargs):
        self.data = kwargs
        super().__init__(**kwargs)

    @property
    def aliases(self):
        return [
            name + '@' + self.data['domain']['name'] for name in self.data['names'][1:]
        ]

    @property
    def mail_address(self):
        return self.data['names'][0] + '@' + self.data['domain']['name']

    @property
    def type(self):
        if self.data['forward']:
            return self.FORWARD
        return self.MAILBOX

    @property
    def type_detail(self):
        if self.type == self.FORWARD:
            return self.data['forward']
        # TODO(@slamora) retrieve mailbox usage
        return {
            'usage': 250,
            'total': 500,
            'unit': 'MB',
            'percent': 50,
        }


class MailinglistService(OrchestraModel):
    api_name = 'mailinglist'
    verbose_name = _('Mailing list')
    description = _('Litle description of what to be expected in this section to aid the user. Even a link to more help if there is one available.')
    fields = ('name', 'status', 'address_name', 'admin_email', 'configure')
    param_defaults = {
        'name': None,
        'is_active': True,
        'admin_email': None,
    }

    def __init__(self, **kwargs):
        self.data = kwargs
        super().__init__(**kwargs)

    @property
    def address_name(self):
        return "{}@{}".format(self.data['address_name'], self.data['address_domain']['name'])

    @property
    def manager_url(self):
        return musician_settings.URL_MAILTRAIN


class SaasService(OrchestraModel):
    api_name = 'saas'
    verbose_name = _('Software as a Service (SaaS)')
    description = _('Litle description of what to be expected in this section to aid the user. Even a link to more help if there is one available.')
    param_defaults = {
        'name': None,
        'service': None,
        'is_active': True,
        'data': {},
    }


class WebSite(OrchestraModel):
    api_name = 'website'
    param_defaults = {
        "id": None,
        "name": None,
        "protocol": None,
        "is_active": True,
        "domains": [],
        "contents": [],
    }

    @classmethod
    def new_from_json(cls, data, **kwargs):
        domains = cls.param_defaults.get("domains")
        if 'domains' in data:
            domains = [Domain.new_from_json(domain_data) for domain_data in data['domains']]

        return super().new_from_json(data=data, domains=domains)
