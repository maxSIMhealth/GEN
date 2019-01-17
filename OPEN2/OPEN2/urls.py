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
from django.urls import path

from forums import views

urlpatterns = [    
    path('', views.home, name='home'),
    path('forums/', views.home, name='home'),
    path('forums/new/', views.new_forum, name='new_forum'),
    path('forums/<int:pk>/', views.forum_comments, name='forum_comments'),
    path('forums/<int:pk>/new_media/', views.new_media, name='new_media'),
    path('forums/<int:pk>/new_comment/', views.new_comment, name='new_comment'),
    # path('forums/<pk>/new/', views.new_comment, name='new_comment'),
    path('admin/', admin.site.urls),
]
