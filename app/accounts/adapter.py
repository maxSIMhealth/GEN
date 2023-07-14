from allauth.account.utils import perform_login
from allauth.exceptions import ImmediateHttpResponse
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

from django.contrib.auth.models import User
from django.shortcuts import render
from GEN import settings as GEN_settings


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom adapter for django-allauth to check if a social account sign in matches an
    existing local user account email. If it does, connect said accounts and
    perform login action.
    """

    def check_social_domain(self, request, social_user):
        """Check if email associated with social account is listed in permitted domains"""
        email_domain = social_user.email.split("@")[1].lower()
        permitted_domains = GEN_settings.VALID_EMAIL_DOMAINS

        if email_domain not in permitted_domains:
            raise ImmediateHttpResponse(
                render(
                    request,
                    "errors/email_domain_not_allowed.html",
                    {"blocked_domain": email_domain},
                )
            )

    def pre_social_login(self, request, sociallogin):
        # social provider user object
        social_user = sociallogin.user

        use_email_domains_whitelist = GEN_settings.USE_EMAIL_DOMAINS_WHITELIST

        # verify if email domain associated with social account is included in whitelist
        if use_email_domains_whitelist:
            self.check_social_domain(request, social_user)

        if social_user.id:
            return
        # check if social provider user object email matches existing local user email
        try:
            user = User.objects.get(email=social_user.email)
            sociallogin.state["process"] = "connect"
            perform_login(request, user, "none")
        except User.DoesNotExist:
            pass
