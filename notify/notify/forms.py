from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordResetForm
from django.core.exceptions import ValidationError
from django import forms
from django.template import loader
from django.utils.translation import gettext_lazy as _
from notify.tasks import send_code_for_verify_email_task, send_notify_of_login_task, send_password_reset_code_task, \
    send_notify_of_unfinished_registration_task

User = get_user_model()


class MyAuthenticationForm(AuthenticationForm):

    def clean(self):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if username is not None and password:
            self.user_cache = authenticate(
                self.request,
                username=username,
                password=password
            )

            if not self.user_cache.email_verify:

                send_notify_of_unfinished_registration_task.delay(
                    username=self.user_cache.username,
                    to_email=self.user_cache.email
                )
                raise ValidationError(
                    "Email not verify! Check your email",
                    code="invalid_login",
                )

            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

                send_notify_of_login_task.delay(
                    username=self.user_cache.username,
                    to_email=self.user_cache.email
                )

        return self.cleaned_data


class MyUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(attrs={"autocomplete": "email"}),
        required=True
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")


class MyPasswordResetForm(PasswordResetForm):
    def send_mail(
            self,
            subject_template_name,
            email_template_name,
            context,
            from_email,
            to_email,
            html_email_template_name=None,
    ):

        # меняем объект модели на конкретное значение для сериализации в json celery
        user = context['user']
        context['user'] = user.username

        subject = loader.render_to_string(subject_template_name, context)
        subject = "".join(subject.splitlines())

        body = loader.render_to_string(email_template_name, context)

        send_password_reset_code_task.delay(subject, body, from_email, to_email,
                                            context, html_email_template_name)

