from django.contrib.auth import views as auth_views
from django.urls import path, re_path, include
from django.conf import settings

from accounts import views as account_views

urlpatterns = [
    path("login/", account_views.Login.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("settings/account", account_views.UserUpdateView.as_view(), name="my_account"),
]

# only allow access if social auth only is DISABLED
if (not settings.USE_SOCIAL_AUTH_ONLY):
    urlpatterns += [
        path("signup/", account_views.signup, name="signup"),
        path("settings/password", account_views.oauth_password, name="oauth_password"),
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
        # account activation
        re_path(
            r"^account_activation_sent/$",
            account_views.account_activation_sent,
            name="account_activation_sent",
        ),
        path(
            "activate/<slug:uidb64>/<slug:token>/", account_views.activate, name="activate",
        ),
    ]

# only allow access if social auth is ENABLED
if (settings.USE_SOCIAL_AUTH):
    urlpatterns += [
        # social login
        path('oauth/', include('social_django.urls', namespace='social')),
        # path("settings/", account_views.settings, name="settings"),
    ]
