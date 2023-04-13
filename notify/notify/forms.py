from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordResetForm
from django.core.exceptions import ValidationError
from django import forms
from django.utils.translation import gettext_lazy as _
from notify.notify import Notify

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
                Notify.send_code_for_verify_email(
                    request=self.request,
                    user=self.user_cache
                )
                raise ValidationError(
                    "Email not verify! Check your email",
                    code="invalid_login",
                )

            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

                Notify.send_notification_about_login(
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
        args = (subject_template_name, email_template_name, context,
                from_email, to_email, html_email_template_name)

        Notify.send_password_reset_code(*args)

