from modeltranslation.admin import TabbedTranslationAdmin

from django.contrib import admin

from .models import Comment, Discussion


def refresh(modeladmin, request, queryset):
    for item in queryset:
        item.save()


refresh.short_description = "Refresh selected items (update content type)"


def duplicate(modeladmin, request, queryset):
    for item in queryset:
        item.duplicate(suffix="(copy)", published=False)


duplicate.short_description = "Duplicate selected items"


class CommentsInline(admin.TabularInline):
    model = Comment
    extra = 0


class DiscussionAdmin(TabbedTranslationAdmin):
    list_filter = (
        "course",
        "published",
        "author",
    )
    list_display = (
        "name",
        "item_type",
        "id",
        "author",
        "course",
        "section",
        "requirement",
        "video",
        "published",
    )
    readonly_fields = (
        "vote_score",
        "num_vote_up",
        "num_vote_down",
        "created",
        "modified",
    )
    inlines = (CommentsInline,)
    actions = [duplicate, refresh]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "description",
                    "author",
                    "course",
                    "section",
                    "requirement",
                    "video",
                    "start_date",
                    "end_date",
                    "show_related_content",
                    "published",
                )
            },
        ),
        (
            "Additional information",
            {
                "fields": (
                    "created",
                    "modified",
                )
            },
        ),
        (
            "Access control",
            {
                "fields": (
                    "access_restriction",
                    "author_access_override",
                )
            },
        ),
        (
            "Voting",
            {
                "fields": (
                    "vote_score",
                    "num_vote_up",
                    "num_vote_down",
                )
            },
        ),
    )


class CommentsAdmin(admin.ModelAdmin):
    # fields = ('author', 'message')
    # filter_horizontal = ('author', )
    fields = (
        "author",
        "discussion",
        "message",
        "vote_score",
        "num_vote_up",
        "num_vote_down",
        "created",
        "modified",
    )
    list_display = ("message", "author", "discussion")
    list_display_links = ("message",)
    list_filter = ("author", "discussion")
    readonly_fields = (
        "vote_score",
        "num_vote_up",
        "num_vote_down",
        "created",
        "modified",
    )


# admin.site.register(MediaFile)
admin.site.register(Discussion, DiscussionAdmin)
admin.site.register(Comment, CommentsAdmin)
