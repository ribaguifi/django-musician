from django.test import TestCase

from .models import UserAccount


class DomainsTestCase(TestCase):
    def test_domain_not_found(self):
        response = self.client.post(
            '/auth/login/',
            {'username': 'admin', 'password': 'admin'},
            follow=True
        )
        self.assertEqual(200, response.status_code)

        response = self.client.get('/domains/3/')
        self.assertEqual(404, response.status_code)


class UserAccountTest(TestCase):
    def test_user_never_logged(self):
        data = {
            'billcontact': {'address': 'foo',
                            'city': 'Barcelona',
                            'country': 'ES',
                            'name': '',
                            'vat': '12345678Z',
                            'zipcode': '08080'},
            'date_joined': '2020-01-14T12:38:31.684495Z',
            'full_name': 'Pep',
            'id': 2,
            'is_active': True,
            'language': 'EN',
            'short_name': '',
            'type': 'INDIVIDUAL',
            'url': 'http://example.org/api/accounts/2/',
            'username': 'pepe'
        }
        account = UserAccount.new_from_json(data)
        self.assertIsNone(account.last_login)
