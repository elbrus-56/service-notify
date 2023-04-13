import sys, os
import django

parent = os.path.abspath("..")
sys.path.insert(1, parent)
sys.path.append("../..")
sys.path.append("../../notify")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.test import TestCase, RequestFactory
from notify.models import User
from notify.notify import Notify


class NotifyTest(TestCase):

    def setUp(self) -> None:
        self.factory = RequestFactory().request()
        self.user = User.objects.create_user(
            username='Qwert', email='qwert@mail.ru', password='121212asasS')

    def test_send_code_for_verify_email(self):
        n = Notify.send_code_for_verify_email(self.factory, self.user)
        self.assertEqual(n.get(), 1)

    def test_send_notification_for_success_registration(self):
        n = Notify.send_notification_for_success_registration(self.user.username, self.user.email)
        self.assertEqual(n.get(), 1)

    def test_send_notification_for_unsuccess_registration(self):
        n = Notify.send_notification_for_unsuccess_registration(self.user.username, self.user.email)
        self.assertEqual(n.get(), 1)

    def test_send_notification_about_login(self):
        n = Notify.send_notification_about_login(self.user.username, self.user.email)
        self.assertEqual(n.get(), 1)

    def test_send_password_reset_code(self):
        n = Notify.send_password_reset_code("registration/password_reset_subject.txt",
                                            "registration/password_reset_email.html",
                                            {'user': self.user, 'domain': 'testserver',
                                             'uid': 'Mw', 'token': 'bmkv76-c4171763fd8e297e74e14d87dde7cf4b',
                                             'protocol': 'http'},
                                            None,
                                            self.user.email,
                                            None)
        self.assertEqual(n.get(), 1)

    def test_send_notification_success_password_reset(self):
        n = Notify.send_notification_success_password_reset(self.user.username, self.user.email)
        self.assertEqual(n.get(), 1)

    def test_send_notification_unsuccess_password_reset(self):
        n = Notify.send_notification_unsuccess_password_reset(self.user.username, self.user.email)
        self.assertEqual(n.get(), 1)
