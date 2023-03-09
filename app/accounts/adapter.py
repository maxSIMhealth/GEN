from allauth.account.utils import perform_login
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth.models import User

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom adapter for django-allauth to check if a social account sign in matches an
    existing local user account email. If it does, connect said accounts and
    perform login action.
    """
    def pre_social_login(self, request, sociallogin):
        # social provider user object
        social_user = sociallogin.user

        if social_user.id:
            return
        # check if social provider user object email matches existing local user email
        try:
            user = User.objects.get(email=social_user.email)
            sociallogin.state['process'] = 'connect'
            perform_login(request, user, 'none')
        except User.DoesNotExist:
            pass
