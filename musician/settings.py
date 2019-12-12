# allowed resources limit hardcoded because cannot be retrieved from the API.
ALLOWED_RESOURCES = {
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
}
