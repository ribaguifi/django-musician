from django.test import TestCase


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
