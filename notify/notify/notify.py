from django.template import loader
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from notify.task import send_email_for_verify_task, \
    send_notification_for_success_registration_task, \
    send_notification_about_login_task, \
    send_password_reset_code_task, \
    send_notification_success_password_reset_task, \
    send_notification_unsuccess_password_reset_task, \
    send_email_task, send_mk_tel_task, sendDocument_task, \
    send_notification_for_unsuccess_registration_task


class Notify:
    @classmethod
    def send_code_for_verify_email(cls, request, user):
        """
        Функция отправляет регистрационный код для подтверждения email
        """
        current_site = get_current_site(request)

        context = {
            'user': user.username,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': default_token_generator.make_token(user),
        }

        message = render_to_string(
            "registration/verify_email.html",
            context=context,
        )

        return send_email_for_verify_task.delay(message, user.email)

    @classmethod
    def send_notification_for_success_registration(cls, username, to_email):
        """
        Функция отправляет уведомление об успешной регистрации
        """
        return send_notification_for_success_registration_task.delay(username, to_email)

    @classmethod
    def send_notification_for_unsuccess_registration(cls, username, to_email):
        """
        Функция отправляет уведомление об ошибке во время регистрации
        """
        return send_notification_for_unsuccess_registration_task.delay(username, to_email)

    @classmethod
    def send_notification_about_login(cls, username, to_email):
        """
        Функция отправляет уведомление о входе в аккаунт
        """
        return send_notification_about_login_task.delay(username, to_email)

    @classmethod
    def send_password_reset_code(cls,
                                 subject_template_name,
                                 email_template_name,
                                 context,
                                 from_email,
                                 to_email,
                                 html_email_template_name
                                 ):
        """
        Функция отправляет код для восстановления пароля
        """

        # меняем объект модели на конкретное значение для сериализации в json celery
        user = context['user']
        context['user'] = user.username

        subject = loader.render_to_string(subject_template_name, context)
        subject = "".join(subject.splitlines())

        body = loader.render_to_string(email_template_name, context)

        return send_password_reset_code_task.delay(subject,
                                                   body,
                                                   from_email,
                                                   to_email,
                                                   html_email_template_name,
                                                   context)

    @classmethod
    def send_notification_success_password_reset(cls, username, to_email):
        """
        Функция отправляет уведомление об успешном изменении пароля
        """
        return send_notification_success_password_reset_task.delay(username, to_email)

    @classmethod
    def send_notification_unsuccess_password_reset(cls, username, to_email):
        """
        Функция отправляет уведомление об ошибке при изменении пароля
        """
        return send_notification_unsuccess_password_reset_task.delay(username, to_email)



    # Уведомления несвязанные с формами регистрации
    @classmethod
    def sendDocument(cls, document_file: str) -> str:
        """Sends document to telegram CHANNEL_ID

        Args:
            document_file (str): path to binary file.

        Returns:
            str: json response
        """
        return sendDocument_task.delay(document_file)

    @classmethod
    def notify(cls, message: str) -> str:
        """Отправка уведомлений (запросов в телеграм канал для отладки)

        Args:
            message (str): сообщение для отправки

        Returns:
            str: ответ api
        """
        return send_mk_tel_task.delay(message)

    @classmethod
    def send_email(cls, subject: str = None, message: str = None, attachments: tuple = None) -> None:
        """Отправка уведомлений на электронную почту

            Args:
                subject (str): тема письма
                message (str): сообщение для отправки
                attachments (tuple): вложения

            Returns:
                int: 1 if True else 0
        """
        return send_email_task.delay(subject, message, attachments)
