from django import forms
from django.conf import settings as django_settings
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, label=_("First name"))
    last_name = forms.CharField(max_length=30, required=True, label=_("Last name"))
    email = forms.EmailField(
        max_length=254, required=True, widget=forms.EmailInput(), label=_("E-mail")
    )
    institution = forms.CharField(max_length=50, label=_("Institution"))

    def clean_email(self):
        """
        Checks if the user email domain is part of the permitted list and
        if it is already registered to another user
        """
        data = self.cleaned_data["email"]
        email_domain = data.split("@")[-1].split(".")[0]

        use_email_domains_whitelist = django_settings.USE_EMAIL_DOMAINS_WHITELIST

        if use_email_domains_whitelist:
            permitted_domains = django_settings.VALID_EMAIL_DOMAINS
            if email_domain not in permitted_domains:
                raise forms.ValidationError(
                    _("E-mail address must be from one of the allowed domains: ")
                    + ", ".join(permitted_domains)
                )

        if User.objects.all().filter(email=data).exists():
            raise forms.ValidationError(_("E-mail address is already being used."))

        return data

    def save(self, request):
        user = super(SignUpForm, self).save(request)
        # set username based on id/pk
        user.username = f"user_{user.id}"
        # save user info to db
        user.save()
        # load the profile instance created by the signal
        user.refresh_from_db()
        # set user institution in auxiliary profile model
        user.profile.institution = self.cleaned_data.get("institution")
        # save update user info to db
        user.save()
        return user

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            # "username",
            "email",
            "institution",
            "password1",
            "password2",
        )
