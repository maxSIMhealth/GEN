from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from .models import Comment, Discussion

# from .models import MediaFile


class CommentsInline(admin.TabularInline):
    model = Comment
    extra = 0


class DiscussionAdmin(TranslationAdmin):
    list_filter = ("course", "published")
    list_display = (
        "name",
        "id",
        "course",
        "section",
        "requirement",
        "video",
        "published",
    )
    readonly_fields = ("vote_score", "num_vote_up", "num_vote_down")
    inlines = (CommentsInline,)


class CommentsAdmin(admin.ModelAdmin):
    # fields = ('author', 'message')
    # filter_horizontal = ('author', )
    list_display = ("message", "author", "discussion")
    list_display_links = ("message",)
    list_filter = ("author", "discussion")


# admin.site.register(MediaFile)
admin.site.register(Discussion, DiscussionAdmin)
admin.site.register(Comment, CommentsAdmin)
