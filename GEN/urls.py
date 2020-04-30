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
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView

from forums import views
from courses import views as course_views
from accounts import views as account_views
from dashboard import views as dashboard_views
from quiz import views as quiz_views

urlpatterns = [
    # path('', views.ForumListView.as_view(), name='home'),
    path('favicon.ico', RedirectView.as_view(
        url=staticfiles_storage.url('im/favicon.ico'))),

    path('', dashboard_views.dashboard, name='home'),
    path('dashboard/', dashboard_views.dashboard, name='dashboard'),

    path('signup/', account_views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # path("settings/", account_views.UserUpdateView.as_view(), name='my_account'),
    path("settings/password", auth_views.PasswordChangeView.as_view(
        template_name='password_change.html'), name="password_change"),
    path("settings/password/done/", auth_views.PasswordChangeDoneView.as_view(
        template_name='password_change_done.html'), name="password_change_done"),
    path("settings/account", account_views.UserUpdateView.as_view(), name='my_account'),
    path("settings/", account_views.settings, name="settings"),
    path("settings/pwd", account_views.password, name="password"),

    path('courses/<int:pk>/', course_views.course, name='course'),
    path('courses/<int:pk>/videos/', views.list_videos, name='list_videos'),
    path('courses/<int:pk>/videos/upload',
         views.upload_video, name='upload_video'),
    path('courses/<int:pk>/videos/<int:video_pk>/comments',
         views.video_comments, name='video_comments'),
    # path('courses/<int:pk>/videos/new/', views.new_media, name='new_media'),
    path('courses/<int:pk>/pdfs/', views.list_pdfs, name='list_pdfs'),
    path('courses/<int:pk>/forums/', views.course_forums, name='course_forums'),
    path('courses/<int:pk>/forums/new/', views.new_forum, name='new_forum'),
    path('courses/<int:pk>/forums/<int:forum_pk>/',
         views.forum_comments, name='forum_comments'),
    path('courses/<int:pk>/forums/<int:forum_pk>/upvote/',
         views.upvote_forum, name='forum_upvote'),
    path('courses/<int:pk>/forums/<int:forum_pk>/clearvote/',
         views.clearvote_forum, name='forum_clearvote'),
    path('courses/<int:pk>/forums/<int:forum_pk>/comment/<int:comment_pk>/upvote/',
         views.upvote_comment, name='comment_upvote'),
    path('courses/<int:pk>/forums/<int:forum_pk>/comment/<int:comment_pk>/clearvote/',
         views.clearvote_comment, name='comment_clearvote'),

    path('courses/<int:pk>/quiz/', views.list_quiz, name='list_quiz'),
    path('courses/<int:pk>/quiz/<int:quiz_pk>/',
         quiz_views.quiz_page, name='quiz'),
    path('courses/<int:pk>/quiz/<int:quiz_pk>/result/',
         quiz_views.quiz_result, name='quiz_result'),

    path('courses/user_attempt/',
         quiz_views.user_attempt, name='quiz_user_attempt'),

    # path('forums/', views.ForumListView.as_view(), name='forums'),

    path('oauth/', include('social_django.urls', namespace='social')),

    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    # access to media files during development
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)

    # django toolbar
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
