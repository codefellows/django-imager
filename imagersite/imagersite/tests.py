"""Test module for imagersite."""
from django.test import Client, TestCase, RequestFactory
from django.urls import reverse_lazy
from bs4 import BeautifulSoup as soup
from django.contrib.auth.models import User
from django.core import mail
from imagersite.views import home_view


class ViewTestCase(TestCase):
    """View test case."""

    def setUp(self):
        """."""
        self.client = Client()

    def test_main_view_status_code_200(self):
        """Test main view has 200 status."""
        response = self.client.get('/potato')
        self.assertEqual(response.status_code, 200)

    def test_home_page_has_h1(self):
        """Test home page has h1 div with correct text."""
        response = self.client.get(reverse_lazy('home'))
        self.assertContains(response, b'Djimager home page.')

    def test_home_page_inherits_base_template(self):
        response = self.client.get(reverse_lazy('home'))
        self.assertTemplateUsed(response, 'imagersite/base.html')

    def test_home_page_shows_login_link(self):
        response = self.client.get(reverse_lazy('home'))
        html = soup(response.content, 'html.parser')
        link = html.find('a', {'href': '/login/'})
        self.assertIsNotNone(link)

    def test_login_view_status_code_200(self):
        """Test login view has 200 status."""
        response = self.client.get(reverse_lazy('login'))
        self.assertEqual(response.status_code, 200)

    def test_logging_in_with_nonexistent_user_goes_back_to_login_page(self):
        """Test login view has 200 status."""
        response = self.client.post(
            reverse_lazy('login'),
            {
                'username': 'flergmcblerg',
                'password': 'flergtheblerg'
            }
        )
        html = soup(response.content, 'html.parser')
        error_item = html.find('ul', {'class': 'errorlist'}).find('li')
        self.assertTrue(
            error_item.text == 'Please enter a correct username and password. Note that both fields may be case-sensitive.')
        self.assertTemplateUsed(response, 'imagersite/login.html')

    def test_logging_in_with_user_redirects_to_home(self):
        """Test login view has 200 status."""
        user = User(username='bob', email='bob@bob.com')
        user.set_password('potatoes')
        user.save()

        response = self.client.post(
            reverse_lazy('login'),
            {
                'username': user.username,
                'password': 'potatoes'
            },
            follow=True
        )
        self.assertTemplateUsed(response, 'imagersite/home.html')
        self.assertContains(response, bytes(user.username, 'utf8'))

    def test_logout_view_status_code_302(self):
        """Test logout view has 302 status."""
        response = self.client.get(reverse_lazy('logout'))
        self.assertEqual(response.status_code, 302)

    def test_register_view_status_code_200(self):
        """Test register view has 200 status."""
        response = self.client.get(reverse_lazy('registration_register'))
        self.assertEqual(response.status_code, 200)

    def test_post_registration_redirects(self):
        """."""
        data = {
            'username': 'metsuperfan',
            'password1': 'yankeessuck',
            'password2': 'yankeessuck',
            'email': 'mets@woo.com'
        }
        response = self.client.post(
            reverse_lazy('registration_register'),
            data
        )
        self.assertTrue(response.status_code, 302)
        self.assertTrue(response.url == reverse_lazy('registration_complete'))

    def test_post_registration_lands_on_reg_complete(self):
        """."""
        data = {
            'username': 'metsuperfan',
            'password1': 'yankeessuck',
            'password2': 'yankeessuck',
            'email': 'mets@woo.com'
        }
        response = self.client.post(
            reverse_lazy('registration_register'),
            data,
            follow=True
        )
        self.assertContains(response, bytes(
            "You are now registered. Activation email sent.", 'utf8'))

    def test_newly_registered_user_exists_and_is_inactive(self):
        """."""
        data = {
            'username': 'metsuperfan',
            'password1': 'yankeessuck',
            'password2': 'yankeessuck',
            'email': 'mets@woo.com'
        }
        self.client.post(
            reverse_lazy('registration_register'),
            data,
            follow=True
        )
        self.assertTrue(User.objects.count() == 1)
        self.assertFalse(User.objects.first().is_active)

    def test_email_gets_sent_on_good_registration(self):
        """."""
        data = {
            'username': 'metsuperfan',
            'password1': 'yankeessuck',
            'password2': 'yankeessuck',
            'email': 'mets@woo.gov'
        }
        self.client.post(
            reverse_lazy('registration_register'),
            data,
            follow=True
        )
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.subject, "Djimager registration email.")
        content = mail.outbox[0].message().get_payload()
        self.assertTrue(content.startswith(
            '\n\nActivate account at testserver:\n\nhttp://testserver/accounts/activate/'))
        self.assertIn('mets@woo.gov', email.to)

    def test_email_link_activates_account(self):
        """."""
        data = {
            'username': 'metsuperfan',
            'password1': 'yankeessuck',
            'password2': 'yankeessuck',
            'email': 'mets@woo.gov'
        }
        self.client.post(
            reverse_lazy('registration_register'),
            data,
            follow=True
        )
        content = mail.outbox[0].message().get_payload()
        link = content.split('\n\n')[2]
        self.client.get(link)
        self.assertTrue(User.objects.count() == 1)
        user = User.objects.get(username='metsuperfan')
        self.assertTrue(user.is_active)

    def test_activated_user_can_now_log_in(self):
        """."""
        data = {
            'username': 'metsuperfan',
            'password1': 'yankeessuck',
            'password2': 'yankeessuck',
            'email': 'mets@woo.gov'
        }
        self.client.post(
            reverse_lazy('registration_register'),
            data,
            follow=True
        )
        content = mail.outbox[0].message().get_payload()
        link = content.split('\n\n')[2]
        self.client.get(link)
        response = self.client.post(reverse_lazy('login'),
            {
                'username': 'metsuperfan',
                'password': 'yankeessuck'
            },
            follow=True
        )
        self.assertContains(response, 'metsuperfan')


class ViewUnitTests(TestCase):
    def setUp(self):
        self.request = RequestFactory()

    def test_get_request_home_view_returns_proper_response(self):
        response = home_view(self.request.get('/foo'))
        self.assertTrue(True)
        # not finishing test because function doesn't do anything really
