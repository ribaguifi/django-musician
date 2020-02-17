from django.test import TestCase

from .models import UserAccount
from .utils import get_bootstraped_percent


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


class GetBootstrapedPercentTest(TestCase):
    BS_WIDTH = [0, 25, 50, 100]

    def test_exact_value(self):
        value = get_bootstraped_percent(25, 100)
        self.assertIn(value, self.BS_WIDTH)
        self.assertEqual(value, 25)

    def test_round_to_lower(self):
        value = get_bootstraped_percent(26, 100)
        self.assertIn(value, self.BS_WIDTH)
        self.assertEqual(value, 25)

    def test_round_to_higher(self):
        value = get_bootstraped_percent(48, 100)
        self.assertIn(value, self.BS_WIDTH)
        self.assertEqual(value, 50)

    def test_max_boundary(self):
        value = get_bootstraped_percent(200, 100)
        self.assertIn(value, self.BS_WIDTH)
        self.assertEqual(value, 100)

    def test_min_boundary(self):
        value = get_bootstraped_percent(-10, 100)
        self.assertIn(value, self.BS_WIDTH)
        self.assertEqual(value, 0)
