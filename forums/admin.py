from django.contrib import admin
from .models import Course, MediaFile, Forum, Comment

admin.site.register(Course)
admin.site.register(MediaFile)
admin.site.register(Forum)
admin.site.register(Comment)