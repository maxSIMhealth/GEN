"""GEN URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import include, path
from django.views.generic.base import RedirectView, TemplateView
from django.views.i18n import JavaScriptCatalog


from accounts import views as account_views
from core import views as core_views
from courses import views as course_views
from dashboard import views as dashboard_views
from discussions import views as discussion_views
from quiz import views as quiz_views
from videos import views as video_views

urlpatterns = [
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
    ),
    path(
        "favicon.ico",
        RedirectView.as_view(url=staticfiles_storage.url("img/favicon.ico")),
    ),
    path("", dashboard_views.dashboard, name="home"),
    path("dashboard/", dashboard_views.dashboard, name="dashboard"),
    path("signup/", account_views.signup, name="signup"),
    path(
        "login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"
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
        auth_views.PasswordChangeView.as_view(template_name="password_change.html"),
        name="password_change",
    ),
    path(
        "settings/password/done/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="password_change_done.html"
        ),
        name="password_change_done",
    ),
    path("settings/account", account_views.UserUpdateView.as_view(), name="my_account"),
    path("courses/<int:pk>/", course_views.course, name="course"),
    # account activation
    url(
        r"^account_activation_sent/$",
        account_views.account_activation_sent,
        name="account_activation_sent",
    ),
    url(
        r"^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$",
        account_views.activate,
        name="activate",
    ),
    # sections
    path(
        "courses/<int:pk>/section/<int:section_pk>/",
        course_views.section_page,
        name="section",
    ),
    # sections > video
    path(
        "courses/<int:pk>/section/<int:section_pk>/upload/",
        video_views.upload_video,
        name="upload_video",
    ),
    path(
        "courses/<int:pk>/section/<int:section_pk>/videos/<int:video_pk>/publish",
        video_views.publish_video,
        name="publish_video",
    ),
    path(
        "courses/<int:pk>/section/<int:section_pk>/videos/<int:video_pk>/unpublish",
        video_views.unpublish_video,
        name="unpublish_video",
    ),
    path(
        "courses/<int:pk>/section/<int:section_pk>/videos/<int:video_pk>/delete",
        video_views.delete_video,
        name="delete_video",
    ),
    path(
        "courses/<int:pk>/section/<int:section_pk>/videos/<int:video_pk>/",
        video_views.video_player,
        name="video_player",
    ),
    # sections > quiz
    path(
        "courses/<int:pk>/section/<int:section_pk>/quiz/<int:quiz_pk>/",
        quiz_views.quiz_page,
        name="quiz",
    ),
    path(
        "courses/<int:pk>/section/<int:section_pk>/quiz/<int:quiz_pk>/result/",
        quiz_views.quiz_result,
        name="quiz_result",
    ),
    # sections > discussion
    path(
        "courses/<int:pk>/section/<int:section_pk>/discussion/new/",
        discussion_views.new_discussion,
        name="new_discussion",
    ),
    path(
        "courses/<int:pk>/section/<int:section_pk>/discussion/<int:discussion_pk>/",
        discussion_views.discussion_comments,
        name="discussion_comments",
    ),
    path(
        "courses/<int:pk>/section/<int:section_pk>/discussion/<int:discussion_pk>/upvote/",
        discussion_views.upvote_discussion,
        name="discussion_upvote",
    ),
    path(
        "courses/<int:pk>/section/<int:section_pk>/discussion/<int:discussion_pk>/clearvote/",
        discussion_views.clearvote_discussion,
        name="discussion_clearvote",
    ),
    path(
        "courses/<int:pk>/section/<int:section_pk>/discussion/<int:discussion_pk>/comment/<int:comment_pk>/upvote/",
        discussion_views.upvote_comment,
        name="comment_upvote",
    ),
    path(
        "courses/<int:pk>/section/<int:section_pk>/discussion/<int:discussion_pk>/comment/<int:comment_pk>/clearvote/",
        discussion_views.clearvote_comment,
        name="comment_clearvote",
    ),
    # admin
    # path("admin/", admin.site.urls),
    # tests
    # path("courses/user_attempt/", quiz_views.user_attempt, name="quiz_user_attempt"),
    # path('oauth/', include('social_django.urls', namespace='social')),
    # FIXME: finish implementing social login
    # path("settings/", account_views.settings, name="settings"),
    # FIXME: video_comment is functional but needs some adjustments and also
    # have to decided if it will continue to exist or not
    # path('courses/<int:pk>/videos/<int:video_pk>/comments',
    #      views.video_comments, name='video_comments'),
    # FIXME: list_pdfs has to be reimplemented
    # path('courses/<int:pk>/pdfs/', views.list_pdfs, name='list_pdfs'),
]

urlpatterns += i18n_patterns(path("admin/", admin.site.urls),)

urlpatterns += i18n_patterns(
    path("jsi18n/", JavaScriptCatalog.as_view(), name="javascript-catalog"),
)

if settings.DEBUG:
    # enable rosetta
    if "rosetta" in settings.INSTALLED_APPS:
        urlpatterns += [url(r"^rosetta/", include("rosetta.urls"))]

    # access to media files during development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # delete user data
    urlpatterns += (path("reset/", core_views.reset, name="reset"),)

    # django toolbar
    import debug_toolbar

    urlpatterns = [path("__debug__/", include(debug_toolbar.urls)),] + urlpatterns
