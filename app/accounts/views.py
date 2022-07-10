import random

from core.models import LoginAlertMessage
from courses.models import Course
from social_django.models import UserSocialAuth

from django.conf import settings as django_settings
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AdminPasswordChangeForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.translation import gettext as _
from django.views.generic import UpdateView

from .forms import SignUpForm
from .tokens import account_activation_token


def random_course_assign(user):
    """Assigns user to random courses until they have reached the max number limit."""

    # FIXME: need to handle case if all courses are full

    # get courses objects
    courses = Course.objects.filter(name__contains="UMontreal")

    # check if any of the courses is full
    for course in courses:
        if course.learners.count() >= course.learners_max_number:
            courses = courses.exclude(pk=course.pk)

    # select a random course from the list and assign participant
    course_selected = random.choice(courses)
    course_selected.members.add(user)
    course_selected.learners.add(user)


class Login(LoginView):
    """Display the login form and handle the login action."""

    template_name = "accounts/login.html"

    use_social_auth = django_settings.USE_SOCIAL_AUTH
    use_social_auth_only = django_settings.USE_SOCIAL_AUTH_ONLY
    social_auth_providers = django_settings.SOCIAL_AUTH_PROVIDERS

    extra_context = {
        "support_emails": django_settings.SUPPORT_EMAILS,
        "use_social_auth": use_social_auth,
        "use_social_auth_only": use_social_auth_only,
        "social_auth_providers": social_auth_providers,
    }

    def get(self, request, *args, **kwargs):
        """Handle GET request. If user is already logged in, redirect to home/dashboard."""
        user = self.request.user

        if user.is_authenticated:
            return redirect("home")

        return self.render_to_response(self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super(Login, self).get_context_data(**kwargs)
        alert_messages = LoginAlertMessage.objects.filter(archived=False)

        for message in alert_messages:
            message.check_if_active()

        alert_messages = alert_messages.filter(archived=False, published=True)

        context["alert_messages"] = alert_messages

        return context


def signup(request):
    """Display the signup form and handle the signup action."""
    if request.method == "POST":
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
            user.profile.institution = form.cleaned_data.get("institution")
            # save update user info to db
            user.save()

            # FIXME: this is temporary, just for the montreal test. It could be ported into an actually feature.
            # assign user to random course
            # user_email_domain = user.email.split("@")[-1].split(".")[0]
            # permitted_domains = ["ontariotechu", "umontreal"]
            # if user_email_domain in permitted_domains:
            #     random_course_assign(user)

            # send account activation email
            current_site = get_current_site(request)
            subject = _("Activate Your GEN Account")
            message = render_to_string(
                "registration/account_activation_email.html",
                {
                    "user": user,
                    "domain": current_site.domain,
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": account_activation_token.make_token(user),
                },
            )
            # from_email = "gen-donotreply@" + current_site.domain
            from_email = django_settings.DEFAULT_FROM_EMAIL
            user.email_user(subject, message, from_email=from_email)

            return redirect("account_activation_sent")
    elif request.user.is_authenticated:
        messages.warning(
            request,
            _("You already have an account."),
        )
        return redirect("home")
    else:
        form = SignUpForm()
    return render(request, "accounts/signup.html", {"form": form})


def account_activation_sent(request):
    debug_mode = django_settings.DEBUG
    return render(
        request,
        "registration/account_activation_sent.html",
        context={"debug_mode": debug_mode},
    )


def activate(request, uidb64, token):
    """Handles validating token link sent by email and activating user account."""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.profile.email_confirmed = True
        user.save()
        # login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        messages.success(
            request, _("Account activated successfully. Please log in into GEN.")
        )
        return redirect("login")
    else:
        messages.warning(
            request,
            _(
                "Try logging in now. The confirmation link has been used or expired. Get in touch if you are having issues: support@maxsimgen.com"
            ),
        )
        return redirect("login")


@method_decorator(login_required, name="dispatch")
class UserUpdateView(UpdateView):
    """Renders page with user profile data and linked social accounts."""

    # FIXME: improve user account info page to allow updating other fields
    model = User
    fields = (
        "first_name",
        "last_name",
    )
    template_name = "accounts/my_account.html"
    success_url = reverse_lazy("my_account")

    def get_context_data(self, **kwargs):
        context = super(UserUpdateView, self).get_context_data(**kwargs)
        user = self.request.user
        social_auth_providers = django_settings.SOCIAL_AUTH_PROVIDERS

        # Social Auth: Google
        try:
            google_login = user.social_auth.get(provider="google-oauth2")
        except UserSocialAuth.DoesNotExist:
            google_login = None

        # Social Auth: Azure AD (Microsoft)
        try:
            azure_login = user.social_auth.get(provider="azuread-oauth2")
        except UserSocialAuth.DoesNotExist:
            azure_login = None

        can_disconnect = user.social_auth.count() > 1 or user.has_usable_password()
        use_social_auth = django_settings.USE_SOCIAL_AUTH
        use_social_auth_only = django_settings.USE_SOCIAL_AUTH_ONLY
        context["google_login"] = google_login
        context["azure_login"] = azure_login
        context["can_disconnect"] = can_disconnect
        context["use_social_auth"] = use_social_auth
        context["use_social_auth_only"] = use_social_auth_only
        context["social_auth_providers"] = social_auth_providers

        return context

    def get_object(self):
        return self.request.user

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        messages.success(request, _("Profile updated successfully."))
        return super().post(request, *args, **kwargs)


@login_required
def oauth_password(request):
    """Handles defining and updating password for users created locally and with OAuth authentication."""
    if request.user.has_usable_password():
        password_form = PasswordChangeForm
    else:
        password_form = AdminPasswordChangeForm

    if request.method == "POST":
        form = password_form(request.user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, _("Your password was successfully updated."))
            return redirect("my_account")
        else:
            messages.error(request, _("Please correct the error below."))
    else:
        form = password_form(request.user)

    return render(request, "accounts/password_change.html", {"form": form})
