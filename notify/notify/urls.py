from django.urls import path, include
from django.views.generic import TemplateView
from notify.views import RegisterView, VerifyEmailView, \
    MyLoginView, MyPasswordResetConfirmView, MyPasswordResetView

urlpatterns = [
    path("login/", MyLoginView.as_view(), name="login"),

    path("register/", RegisterView.as_view(), name="register"),

    path("confirm_email/", TemplateView.as_view(
        template_name="registration/confirm_email.html"),
         name="confirm_email"),

    path("invalid_verify/", TemplateView.as_view(
        template_name="registration/invalid_verify.html"),
         name="invalid_verify"),

    path("verify_email/<uidb64>/<token>/",
         VerifyEmailView.as_view(),
         name="verify_email"),

    path(
        "reset/<uidb64>/<token>/",
        MyPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),

    path("password_reset/",
         MyPasswordResetView.as_view(),
         name="password_reset"),

    path("", include("django.contrib.auth.urls"))

]
