# Сервис нотификации

Реализованы: форма регистрации с верификацией емайл, форма аутентификации, форма восстановления пароля
Все уведомления автоматически отправляются при вводе данных в форму.

Модель User использую свою, с добавлением поля верификацией email.

Результат выводится в консоль Worker Celery



    Реализовано:

1. Отправка кода регистрации на email
2. Отправка уведомления об успешной регистрации на email
3. Отправка уведомления об ошибке во время регистрации на email
4. Отправка уведомления о входе в аккаунт (Оповещение безопасности) на email
5. Отправка кода для восстановления пароля на email
6. Отправка уведомления об успешном изменении пароля на email
7. Отправка уведомления об ошибке при изменении пароля на email
# Не связано с регистрацией
8. Отправка файловых и текстовых уведомлений на email
9. Отправка документов в телеграм
10. Отправка текстовых уведомлений в телеграм

# Запуск
python 3.8.5

redis-server --port 6385
python -m celery -A config worker -E
python -m manage.py runserver 5000


# Тесты

/tests/test_notify.py

Результат выводится в консоль Worker Celery















# Установка

1. Для начала склонируйте репозиторий:
```

```

2. Создайте виртуальное окружение:
```
py -m venv venv
```

3. Активируйте виртуальное окружение:
```
source venv/bin/activate
```

4. Установите необходимые зависимости из requirements.txt:
```
pip install -r requirements.txt
```

5. Создайте файл переименуйте файл example.env в .env и укажите необходимые значения переменных окружения.

6. Время проводить миграции для базы данных:
```
py manage.py migrate
```

7. Чтобы использовать админ-панель, необходимо создать суперпользователя посредством
команды ```python manage.py createsuperuser```. Валидация паролей отключена.

8. Далее мы запускаем сервер:
```
nohup python manage.py runserver 8035
```
gunicorn --bind 127.0.0.1:8035 config.wsgi



9. Для просмотра документации перейдите по адресу: localhost:8000/swagger/
# deploy 

