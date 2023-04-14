import json
import requests

from config.celery import app
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template import loader


@app.task()
def send_code_for_verify_email_task(message, email):
    """
     Функция отправляет регистрационный код для подтверждения email
    """

    email = EmailMessage(
        subject='Подтверждение регистрации',
        body=message,
        to=[email],
    )
    print("send_email_for_verify_task")
    return email.send(fail_silently=False)


@app.task()
def send_notify_of_unfinished_registration_task(username, to_email):
    """
    Функция отправляет уведомление о незавершенной регистрации
    """

    email = EmailMessage(
        subject="Завершите регистрацию!",
        body=f"{username}, вы не сможете войти в учетную запись, пока не подтвердите свой email",
        to=[to_email],
    )

    print("send_notify_of_unfinished_registration_task")
    return email.send(fail_silently=False)


@app.task()
def send_notify_of_success_registration_task(username, to_email):
    """
    Функция отправляет уведомление об успешной регистрации
    """

    email = EmailMessage(
        subject="Благодарим за регистрацию!",
        body=f"{username}, Ваша учетная запись успешно зарегистрирована",
        to=[to_email],
    )

    print("send_notification_for_success_registration_task")
    return email.send(fail_silently=False)


@app.task()
def send_notify_of_unsuccess_registration_task(username, to_email):
    """
    Функция отправляет уведомление об ошибке во время регистрации
    """

    email = EmailMessage(
        subject="Произошла ошибка во время регистрации!",
        body=f"{username}, Произошла ошибка во время регистрации, повторите попытку",
        to=[to_email],
    )

    print("send_notification_for_unsuccess_registration_task")
    return email.send(fail_silently=False)


@app.task()
def send_notify_of_login_task(username, to_email):
    """
    Функция отправляет уведомление о входе в аккаунт
    """

    email = EmailMessage(
        subject="Оповещение системы безопасности",
        body=f"Здравствуйте, {username}! Вход в учетную запись выполнен успешно. Если это были не вы, "
             f"срочно смените пароль",
        to=[to_email],
    )

    print("send_notification_about_login_task")
    return email.send(fail_silently=False)


@app.task()
def send_password_reset_code_task(subject,
                                  body,
                                  from_email,
                                  to_email,
                                  context,
                                  html_email_template_name
                                  ):
    """
    Функция отправляет код для восстановления пароля
    """

    email = EmailMultiAlternatives(subject, body, from_email, [to_email])

    if html_email_template_name is not None:
        html_email = loader.render_to_string(html_email_template_name, context)
        email.attach_alternative(html_email, "text/html")

    print("send_password_reset_code_task")
    return email.send(fail_silently=False)


@app.task()
def send_notify_of_success_password_reset_task(username, to_email):

    """
    Функция отправляет уведомление об успешном изменении пароля
    """

    email = EmailMessage(
        subject="Пароль успешно изменен",
        body=f"Здравствуйте, {username}, пароль учетной записи был успешно изменен",
        to=[to_email],
    )

    print("send_notification_success_password_reset_task")
    return email.send(fail_silently=False)


@app.task()
def send_notify_of_unsuccess_password_reset_task(username, to_email):

    """
    Функция отправляет уведомление об ошибке при изменении пароля
    """

    email = EmailMessage(
        subject="Внимание! Пароль не был изменен.",
        body=f"Здравствуйте, {username}, возникла ошибка при изменении пароля. Повторите попытку.",
        to=[to_email],
    )

    print("send_notification_unsuccess_password_reset_task")
    return email.send(fail_silently=False)


# Не связано с регистрацией
@app.task
def send_email_task(subject: str = None, message: str = None, attachments: tuple = None):
    """
    Отправка уведомлений на электронную почту

    Args:
        subject (str): тема письма
        message (str): сообщение для отправки
        attachments (tuple): вложения

    Returns:
        int: 1 if True else 0
    """
    to_email = ""

    email = EmailMessage(
        subject=subject,
        body=message,
        to=to_email,
    )

    if attachments:
        filename, content, mimetype = attachments
        try:
            with open(content, "rb") as file:
                content = file.read()
        except (Exception,):
            print(f"Файл {content} не найден")
        email.attach(filename, content, mimetype)

    return email.send(fail_silently=False)


@app.task
def send_mk_tel_task(text: str):

    """Отправляем в Телеграмм Канал"""

    import requests
    api_token = ''  # указывается в settings
    requests.get('https://api.telegram.org/bot{}/sendMessage'.format(api_token), params=dict(
        chat_id='',
        text=text))


@app.task
def sendDocument_task(document_file: str):
    """Sends document to telegram CHANNEL_ID

    Args:
        document_file (str): path to binary file.

    Returns:
        str: json response
    """

    # заглушки
    TELEGRAM_BOT_TOKEN = ""  # указывается в settings
    CHANNEL_ID = ""          # указывается в settings

    document = open(document_file, "rb")
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
    response = requests.post(
        url, data={"chat_id": CHANNEL_ID}, files={"document": document}
    )
    content = response.content.decode("utf8")
    js = json.loads(content)
    return js
