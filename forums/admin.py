from django.contrib import admin

from .models import MediaFile, Forum, Comment


class CommentsAdmin(admin.ModelAdmin):
    # fields = ('author', 'message')
    # filter_horizontal = ('author', )
    list_display = ('author', 'message', 'forum')
    list_display_links = ('message', )
    list_filter = ('author', 'forum')


admin.site.register(MediaFile)
admin.site.register(Forum)
admin.site.register(Comment, CommentsAdmin)
