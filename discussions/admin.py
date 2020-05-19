from django.contrib import admin

from .models import Comment, Discussion

# from .models import MediaFile


class CommentsAdmin(admin.ModelAdmin):
    # fields = ('author', 'message')
    # filter_horizontal = ('author', )
    list_display = ("author", "message", "discussion")
    list_display_links = ("message",)
    list_filter = ("author", "discussion")


# admin.site.register(MediaFile)
admin.site.register(Discussion)
admin.site.register(Comment, CommentsAdmin)
