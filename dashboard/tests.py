from django.urls import reverse
from django.test import TestCase

class DashboardTests(TestCase):
    def test_dashboard_view_status_code_not_logged(self):
        url = reverse('dashboard')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 302)