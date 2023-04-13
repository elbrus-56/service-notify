from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import LoginView, PasswordResetView, \
    PasswordResetConfirmView
from django.core.exceptions import ValidationError, ImproperlyConfigured
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, resolve_url
from django.utils.decorators import method_decorator
from django.utils.http import urlsafe_base64_decode
from django.views import View
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters

from notify.forms import MyAuthenticationForm, MyUserCreationForm, \
    MyPasswordResetForm
from notify.notify import Notify

User = get_user_model()


class MyLoginView(LoginView):
    form_class = MyAuthenticationForm


class RegisterView(View):
    template_name = "registration/register.html"

    def get(self, request):
        context = {
            "form": MyUserCreationForm()
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = MyUserCreationForm(request.POST)

        if form.is_valid():
            form.save()

            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password1")
            user = authenticate(email=email, password=password)

            Notify.send_code_for_verify_email(request, user)

            return redirect('confirm_email')

        context = {
            "form": MyUserCreationForm()
        }
        return render(request, self.template_name, context)


class VerifyEmailView(View):
    def get(self, request, uidb64, token):
        user = self.get_user(uidb64)

        if user is not None and default_token_generator.check_token(user, token):
            user.email_verify = True
            user.save()
            login(request, user)

            Notify.send_notification_for_success_registration(
                username=user.username,
                to_email=user.email
            )

            return redirect("home")

        Notify.send_notification_for_unsuccess_registration(
            username=user.username,
            to_email=user.email
        )
        return redirect("invalid_verify")

    @staticmethod
    def get_user(uidb64):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (
                TypeError,
                ValueError,
                OverflowError,
                User.DoesNotExist,
                ValidationError,
        ):
            user = None
        return user


class MyPasswordResetView(PasswordResetView):
    form_class = MyPasswordResetForm


INTERNAL_RESET_SESSION_TOKEN = "_password_reset_token"


class MyPasswordResetConfirmView(PasswordResetConfirmView):

    @method_decorator(sensitive_post_parameters())
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        if "uidb64" not in kwargs or "token" not in kwargs:
            raise ImproperlyConfigured(
                "The URL path must contain 'uidb64' and 'token' parameters."
            )

        self.validlink = False
        self.user = self.get_user(kwargs["uidb64"])

        if self.user is not None:
            token = kwargs["token"]
            if token == self.reset_url_token:
                session_token = self.request.session.get(INTERNAL_RESET_SESSION_TOKEN)
                if self.token_generator.check_token(self.user, session_token):
                    # If the token is valid, display the password reset form.
                    self.validlink = True
                    return super().dispatch(*args, **kwargs)

            else:
                if self.token_generator.check_token(self.user, token):
                    # Store the token in the session and redirect to the
                    # password reset form at a URL without the token. That
                    # avoids the possibility of leaking the token in the
                    # HTTP Referer header.
                    self.request.session[INTERNAL_RESET_SESSION_TOKEN] = token
                    redirect_url = self.request.path.replace(
                        token, self.reset_url_token
                    )
                    Notify.send_notification_success_password_reset(self.user.username, self.user.email)
                    return HttpResponseRedirect(redirect_url)

        # Display the "Password reset unsuccessful" page.
        Notify.send_notification_unsuccess_password_reset(self.user.username, self.user.email)
        return self.render_to_response(self.get_context_data())

    def get_user(self, uidb64):
        try:
            # urlsafe_base64_decode() decodes to bytestring
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (
                TypeError,
                ValueError,
                OverflowError,
                User.DoesNotExist,
                ValidationError,
        ):
            user = None
        return user
