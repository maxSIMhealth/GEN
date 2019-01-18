from django.contrib import admin
from .models import Forum, Comment

admin.site.register(Forum)
admin.site.register(Comment)