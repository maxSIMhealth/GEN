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
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import include, path
from django.views.generic.base import RedirectView

from accounts import views as account_views
from courses import views as course_views
from dashboard import views as dashboard_views
from forums import views as forum_views
from quiz import views as quiz_views
from videos import views as video_views

urlpatterns = [
    # path('', views.ForumListView.as_view(), name='home'),
    path(
        "favicon.ico",
        RedirectView.as_view(url=staticfiles_storage.url("im/favicon.ico")),
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
    # FIXME: finish implementing social login
    # path("settings/", account_views.settings, name="settings"),
    path("courses/<int:pk>/", course_views.course, name="course"),
    path("courses/<int:pk>/videos/", video_views.list_videos, name="list_videos"),
    path(
        "courses/<int:pk>/videos/upload", video_views.upload_video, name="upload_video"
    ),
    path(
        "courses/<int:pk>/videos/<int:video_pk>/delete",
        video_views.delete_video,
        name="delete_video",
    ),
    path(
        "courses/<int:pk>/videos/<int:video_pk>/",
        video_views.video_player,
        name="video_player",
    ),
    # FIXME: video_comment is functional but needs some adjustments and also
    # have to decided if it will continue to exist or not
    # path('courses/<int:pk>/videos/<int:video_pk>/comments',
    #      views.video_comments, name='video_comments'),
    # FIXME: list_pdfs has to be reimplemented
    # path('courses/<int:pk>/pdfs/', views.list_pdfs, name='list_pdfs'),
    path("courses/<int:pk>/forums/", forum_views.course_forums, name="course_forums"),
    path("courses/<int:pk>/forums/new/", forum_views.new_forum, name="new_forum"),
    path(
        "courses/<int:pk>/forums/<int:forum_pk>/",
        forum_views.discussion_comments,
        name="discussion_comments",
    ),
    path(
        "courses/<int:pk>/forums/<int:forum_pk>/upvote/",
        forum_views.upvote_forum,
        name="forum_upvote",
    ),
    path(
        "courses/<int:pk>/forums/<int:forum_pk>/clearvote/",
        forum_views.clearvote_forum,
        name="forum_clearvote",
    ),
    path(
        "courses/<int:pk>/forums/<int:forum_pk>/comment/<int:comment_pk>/upvote/",
        forum_views.upvote_comment,
        name="comment_upvote",
    ),
    path(
        "courses/<int:pk>/forums/<int:forum_pk>/comment/<int:comment_pk>/clearvote/",
        forum_views.clearvote_comment,
        name="comment_clearvote",
    ),
    path("courses/<int:pk>/quiz/", quiz_views.list_quiz, name="list_quiz"),
    path("courses/<int:pk>/quiz/<int:quiz_pk>/", quiz_views.quiz_page, name="quiz"),
    path(
        "courses/<int:pk>/quiz/<int:quiz_pk>/result/",
        quiz_views.quiz_result,
        name="quiz_result",
    ),
    path("courses/user_attempt/", quiz_views.user_attempt, name="quiz_user_attempt"),
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
    path(
        "courses/<int:pk>/section/<int:section_pk>/",
        course_views.section_page,
        name="section",
    ),
    # path('forums/', views.ForumListView.as_view(), name='forums'),
    # path('oauth/', include('social_django.urls', namespace='social')),
    path("admin/", admin.site.urls),
]

if settings.DEBUG:
    # access to media files during development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # django toolbar
    import debug_toolbar

    urlpatterns = [path("__debug__/", include(debug_toolbar.urls)),] + urlpatterns
