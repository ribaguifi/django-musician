from django.utils.html import format_html


class Service:
    api_name = None
    verbose_name = None
    fields = ()

    def __init__(self, data={}):
        if self.verbose_name is None:
            self.verbose_name = self.api_name

        self.data = data

    def get(self, key):
        # retrieve attr of the object and if undefined get raw data
        return getattr(self, key, self.data.get(key))


class MailService(Service):
    api_name = 'address'
    verbose_name = 'Mail'
    fields = ('mail_address', 'aliases', 'type', 'type_detail')

    FORWARD = 'forward'
    MAILBOX = 'mailbox'

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
        return {'usage': 0, 'total': 213}


class MailinglistService(Service):
    api_name = 'mailinglist'
    verbose_name = 'Mailing list'
    fields = ('name', 'status', 'address_name', 'admin_email', 'configure')

    @property
    def status(self):
        # TODO(@slamora): where retrieve if the list is active?
        return 'active'

    @property
    def address_name(self):
        return "{}@{}".format(self.data['address_name'], self.data['address_domain']['name'])

    @property
    def configure(self):
        # TODO(@slamora): build mailtran absolute URL
        return format_html('<a href="#TODO">Mailtrain</a>')
