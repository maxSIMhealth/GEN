from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(
        max_length=254,
        required=True,
        widget=forms.EmailInput()
    )
    institution = forms.CharField(max_length=50)

    def clean_email(self):
        """
        Checks if the user email domain is part of the permitted list and
        if it is already registered to another user
        """
        data = self.cleaned_data['email']
        email_domain = data.split('@')[-1].split('.')[0]
        permitted_domains = ['ontariotechu', 'umontreal']
        if email_domain not in permitted_domains:   # any check you need
            raise forms.ValidationError(
                "E-mail address must be from one of the allowed domains: "
                + ", ".join(permitted_domains))

        if User.objects.all().filter(email=data).exists():
            raise forms.ValidationError(
                "E-mail address is already being used.")

        return data

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username',
                  'email', 'institution',
                  'password1', 'password2')
