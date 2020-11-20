from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


class CoreTests(TestCase):
    # @classmethod
    # def setUpTestData(cls):
    #     print("setUpTestData: Run once to set up non-modified data for all class methods.")
    #     pass
    #
    # def setUp(self):
    #     print("setUp: Run once for every test method to setup clean data.")
    #     pass

    ### Login

    def test_login_view_url_accessible_by_name(self):
        url = reverse('login')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_login_view_url_exists_at_desired_location_redirect(self):
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 301)

    def test_login_view_uses_correct_template(self):
        url = reverse('login')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    ### Home / Dashboard

    def test_home_view_url_accessible_by_name_redirect(self):
        url = reverse('home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_home_url_exists_at_desired_location_redirect(self):
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 301)

    # def test_home_view_status_code_not_logged(self):
    #     print("VIEW: home - not logged")
    #     url = reverse("home")
    #     response = self.client.get(url)
    #     self.assertEquals(response.status_code, 302)
    #
    # def test_login_view_status_code_not_logged(self):
    #     print("VIEW: login - not logged")
    #     url = reverse("login")
    #     response = self.client.get(url)
    #     self.assertEquals(response.status_code, 200)

class CoreTestsLoggedIn(TestCase):
    def setUp(self):
        # create test user
        test_user1 = User.objects.create_user(username="test_user1", password="`6Wg).r.,e2RU>\q")
        # test_user1.set_password("`6Wg).r.,e2RU>\q")
        test_user1.save()

        # create course
        # FIXME: implement this

        # assign test user to course
        # FIXME: implement this

    def test_redirect_if_not_logged_in(self):
        url = reverse("home")
        response = self.client.get(url)
        self.assertRedirects(response, "/login/?next=/")

    def test_logged_in_uses_correct_template(self):
        logged_in = self.client.login(username="test_user1", password="`6Wg).r.,e2RU>\q")
        url = reverse("home")
        response = self.client.get(url)

        # check if user is logged in successfully
        self.assertEqual(str(response.context['user']), "test_user1")

        # check if page response is "success"
        self.assertEqual(response.status_code, 200)

        # check if page is using the correct template
        self.assertTemplateUsed(response, "dashboard.html")

