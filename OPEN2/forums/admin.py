from django.contrib import admin
from .models import Forum, AttachmentKind, Comment

admin.site.register(Forum)
admin.site.register(AttachmentKind)
admin.site.register(Comment)