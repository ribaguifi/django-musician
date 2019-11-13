class MailService:
    name = 'address'
    verbose_name = 'Mail'
    fields = ('mail_address', 'aliases', 'type', 'type_detail')

    FORWARD = 'forward'
    MAILBOX = 'mailbox'

    def __init__(self, data={}):
        if self.verbose_name is None:
            self.verbose_name = self.name

        self.data = data

    def get(self, key):
        # retrieve attr of the object and if undefined get raw data
        return getattr(self, key, self.data.get(key))

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
