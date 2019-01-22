"""OPEN2 URL Configuration

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
from django.conf.urls import url
from django.urls import path, include
from django.contrib.auth import views as auth_views

from accounts import views as account_views
from forums import views

urlpatterns = [    
    path('', views.ForumListView.as_view(), name='home'),
    path('signup/', account_views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path("settings/password", auth_views.PasswordChangeView.as_view(template_name='password_change.html'), name="password_change"),
    path("settings/password/done", auth_views.PasswordChangeDoneView.as_view(template_name='password_change_done.html'), name="password_change_done"),
    path("settings/account", account_views.UserUpdateView.as_view(), name='my_account'),
    path('forums/', views.ForumListView.as_view(), name='home'),
    path('forums/new/', views.new_forum, name='new_forum'),
    path('forums/<int:pk>/', views.forum_comments, name='forum_comments'),
    path('forums/<int:pk>/upvote', views.upvote, name='forum_upvote'),
    # path('forums/<int:pk>/downvote', views.downvote, name='forum_downvote'),
    path('forums/<int:pk>/clearvote', views.clearvote, name='forum_clearvote'),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns