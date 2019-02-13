from django.contrib import admin

from .models import MediaFile, Forum, Comment


admin.site.register(MediaFile)
admin.site.register(Forum)
admin.site.register(Comment)
