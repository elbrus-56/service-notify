import json
import requests
from config.celery import app
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template import loader


@app.task()
def send_email_for_verify_task(message, to_email):
    email = EmailMessage(
        subject='Подтверждение регистрации',
        body=message,
        to=[to_email],
    )
    print("send_email_for_verify_task")
    return email.send(fail_silently=False)


@app.task()
def send_notification_for_success_registration_task(username, to_email):
    email = EmailMessage(
        subject="Благодарим за регистрацию!",
        body=f"{username}, Ваша учетная запись успешно зарегистрирована",
        to=[to_email],
    )

    print("send_notification_for_success_registration_task")
    return email.send(fail_silently=False)


@app.task()
def send_notification_for_unsuccess_registration_task(username, to_email):
    email = EmailMessage(
        subject="Произошла ошибка во время регистрации!",
        body=f"{username}, Произошла ошибка во время регистрации, повторите попытку",
        to=[to_email],
    )

    print("send_notification_for_unsuccess_registration_task")
    return email.send(fail_silently=False)


@app.task()
def send_notification_about_login_task(username, to_email):
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
                                  html_email_template_name,
                                  context
                                  ):
    email = EmailMultiAlternatives(subject, body, from_email, [to_email])

    if html_email_template_name is not None:
        html_email = loader.render_to_string(html_email_template_name, context)
        email.attach_alternative(html_email, "text/html")

    print("send_password_reset_code_task")
    return email.send(fail_silently=False)


@app.task()
def send_notification_success_password_reset_task(username, to_email):
    email = EmailMessage(
        subject="Пароль успешно изменен",
        body=f"Здравствуйте, {username}, пароль учетной записи был успешно изменен",
        to=[to_email],
    )

    print("send_notification_success_password_reset_task")
    return email.send(fail_silently=False)


@app.task()
def send_notification_unsuccess_password_reset_task(username, to_email):
    email = EmailMessage(
        subject="Внимание! Пароль не был изменен.",
        body=f"Здравствуйте, {username}, возникла ошибка при изменении пароля. Повторите попытку.",
        to=[to_email],
    )

    print("send_notification_unsuccess_password_reset_task")
    return email.send(fail_silently=False)


@app.task
def send_email_task(subject, message, attachments):
    # Заглушки
    from_email = ""
    to_email = ""

    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=from_email,
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
    api_token = ''
    requests.get('https://api.telegram.org/bot{}/sendMessage'.format(api_token), params=dict(
        chat_id='',
        text=text))


@app.task
def sendDocument_task(document_file):
    # заглушки
    TELEGRAM_BOT_TOKEN = ""
    CHANNEL_ID = ""

    document = open(document_file, "rb")
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
    response = requests.post(
        url, data={"chat_id": CHANNEL_ID}, files={"document": document}
    )
    content = response.content.decode("utf8")
    js = json.loads(content)
    return js
