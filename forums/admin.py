from django.contrib import admin
from .models import Course, Forum, Comment

admin.site.register(Course)
admin.site.register(Forum)
admin.site.register(Comment)