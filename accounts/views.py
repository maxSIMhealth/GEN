from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.forms import AdminPasswordChangeForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.encoding import force_text, force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.generic import UpdateView
from django.template.loader import render_to_string

from social_django.models import UserSocialAuth

from .forms import SignUpForm
from .tokens import account_activation_token


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            # create user but don't save to DB yet
            user = form.save(commit=False)
            # set user as inactive
            user.is_active = False
            # save user info to db
            user.save()
            # load the profile instance created by the signal
            user.refresh_from_db()
            # set user institution in auxiliary profile model
            user.profile.institution = form.cleaned_data.get('institution')
            # save update user info to db
            user.save()

            # send account activation email
            current_site = get_current_site(request)
            subject = 'Activate Your GEN Account'
            message = render_to_string('account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            user.email_user(subject, message,
                            from_email='gen@andreitorres.tech')

            return redirect('account_activation_sent')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


def account_activation_sent(request):
    return render(request, 'account_activation_sent.html')


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.profile.email_confirmed = True
        user.save()
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect('home')
        # FIXME: finish implementing 'activation confirmed' page
        # return render(request, 'account_activation_valid.html')
    else:
        return render(request, 'account_activation_invalid.html')


@login_required
def settings(request):
    user = request.user

    try:
        github_login = user.social_auth.get(provider='github')
    except UserSocialAuth.DoesNotExist:
        github_login = None

    try:
        google_login = user.social_auth.get(provider='google-oauth2')
    except UserSocialAuth.DoesNotExist:
        google_login = None

    # try:
    #     twitter_login = user.social_auth.get(provider='twitter')
    # except UserSocialAuth.DoesNotExist:
    #     twitter_login = None

    # try:
    #     facebook_login = user.social_auth.get(provider='facebook')
    # except UserSocialAuth.DoesNotExist:
    #     facebook_login = None

    can_disconnect = (user.social_auth.count() >
                      1 or user.has_usable_password())

    return render(request, 'settings.html', {
        'github_login': github_login,
        'google_login': google_login,
        # 'twitter_login': twitter_login,
        # 'facebook_login': facebook_login,
        'can_disconnect': can_disconnect
    })


@method_decorator(login_required, name='dispatch')
class UserUpdateView(UpdateView):
    # FIXME: improve user account info page to allow updating profile fields
    model = User
    fields = ('first_name', 'last_name', )
    template_name = 'my_account.html'
    success_url = reverse_lazy('home')

    def get_object(self):
        return self.request.user
