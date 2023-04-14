import sys, os
import django

parent = os.path.abspath("..")
sys.path.insert(1, parent)
sys.path.append("../..")
sys.path.append("../../notify")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.test import TestCase
from django.contrib.auth.models import User
from notify.tasks import send_code_for_verify_email_task, \
    send_notify_of_success_registration_task, \
    send_notify_of_unsuccess_registration_task, \
    send_notify_of_login_task, send_password_reset_code_task, \
    send_notify_of_success_password_reset_task, \
    send_notify_of_unsuccess_password_reset_task, \
    send_notify_of_unfinished_registration_task


class NotifyTest(TestCase):

    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username='Qwert', email='test@test.test', password='121212asasS')
        self.message = f"Здравствуйте, {self.user.username}, для завершения регистрации перейдите по ссылке: \
        http://127.0.0.1:5000/verify_email/OA/bmmwnv-6298e5cb52398c452cbb8b7446213569/"

    def test_send_code_for_verify_email(self):
        n = send_code_for_verify_email_task.delay(self.message, self.user.email)
        self.assertEqual(1, n.get())

    def test_send_notify_of_success_registration_task(self):
        n = send_notify_of_success_registration_task.delay(self.user.username, self.user.email)
        self.assertEqual(1, n.get())

    def test_send_notify_of_unsuccess_registration_task(self):
        n = send_notify_of_unsuccess_registration_task.delay(self.user.username, self.user.email)
        self.assertEqual(1, n.get())

    def test_send_notify_of_login_task(self):
        n = send_notify_of_login_task.delay(self.user.username, self.user.email)
        self.assertEqual(1, n.get())

    def test_send_notify_of_unfinished_registration_task(self):
        n = send_notify_of_unfinished_registration_task.delay(self.user.username, self.user.email)
        self.assertEqual(1, n.get())

    def test_send_password_reset_code_task(self):
        n = send_password_reset_code_task.delay(subject="Восстановление пароля",
                                                body=self.message,
                                                from_email="mk@xn--e1ajbcdqnp9g.xn--p1ai",
                                                to_email=self.user.email,
                                                context={},
                                                html_email_template_name=None)
        self.assertEqual(1, n.get())

    def test_send_notification_success_password_reset(self):
        n = send_notify_of_success_password_reset_task.delay(self.user.username, self.user.email)
        self.assertEqual(1, n.get())

    def test_send_notification_unsuccess_password_reset(self):
        n = send_notify_of_unsuccess_password_reset_task.delay(self.user.username, self.user.email)
        self.assertEqual(1, n.get())
