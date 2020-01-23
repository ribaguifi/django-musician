from django.conf import settings


def getsetting(name):
    return getattr(settings, name, DEFAULTS.get(name))


DEFAULTS = {
    # allowed resources limit hardcoded because cannot be retrieved from the API.
    "ALLOWED_RESOURCES": {
        'INDIVIDUAL':
        {
            # 'disk': 1024,
            # 'traffic': 2048,
            'mailbox': 2,
        },
        'ASSOCIATION': {
            # 'disk': 5 * 1024,
            # 'traffic': 20 * 1024,
            'mailbox': 10,
        }
    },
    "URL_DB_PHPMYADMIN": "https://www.phpmyadmin.net/",
    "URL_MAILTRAIN": "https://mailtrain.org/",
    "URL_SAAS_GITLAB": "https://gitlab.org/",
    "URL_SAAS_OWNCLOUD": "https://owncloud.org/",
    "URL_SAAS_WORDPRESS": "https://wordpress.org/",
}

ALLOWED_RESOURCES = getsetting("ALLOWED_RESOURCES")

URL_DB_PHPMYADMIN = getsetting("URL_DB_PHPMYADMIN")

URL_MAILTRAIN = getsetting("URL_MAILTRAIN")

URL_SAAS_GITLAB = getsetting("URL_SAAS_GITLAB")

URL_SAAS_OWNCLOUD = getsetting("URL_SAAS_OWNCLOUD")

URL_SAAS_WORDPRESS = getsetting("URL_SAAS_WORDPRESS")
