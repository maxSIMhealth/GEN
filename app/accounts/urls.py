from django.contrib.auth import views as auth_views
from django.urls import path, re_path

from accounts import views as account_views

urlpatterns = [
    path("signup/", account_views.signup, name="signup"),
    path(
        "login/", account_views.Login.as_view(template_name="login.html"), name="login"
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    # path("settings/", account_views.UserUpdateView.as_view(), name='my_account'),
    path(
        "password_reset/",
        auth_views.PasswordResetView.as_view(),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    path(
        "settings/password",
        auth_views.PasswordChangeView.as_view(template_name="accounts/password_change.html"),
        name="password_change",
    ),
    path(
        "settings/password/done/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="accounts/password_change_done.html"
        ),
        name="password_change_done",
    ),
    path("settings/account", account_views.UserUpdateView.as_view(), name="my_account"),

    # account activation
    re_path(
        r"^account_activation_sent/$",
        account_views.account_activation_sent,
        name="account_activation_sent",
    ),
    path(
      "activate/<slug:uidb64>/<slug:token>/", account_views.activate, name="activate",
    ),

    # tests / WIP
    # FIXME: finish implementing social login
    # path('oauth/', include('social_django.urls', namespace='social')),
    # path("settings/", account_views.settings, name="settings"),
]