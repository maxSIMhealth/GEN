from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin
from django.contrib import admin
from modeltranslation.admin import TabbedTranslationAdmin

from .forms import VideoFileAdminForm
from .models import Playlist, VideoFile


def refresh(modeladmin, request, queryset):
    for item in queryset:
        item.save()


refresh.short_description = "Refresh selected items (update content type)"


def update_thumbnails(modeladmin, request, queryset):
    for item in queryset:
        item.generate_video_thumbnail()


update_thumbnails.short_description = "Update thumbnail of selected videos"


def duplicate(modeladmin, request, queryset):
    for item in queryset:
        item.duplicate(suffix="(copy)", published=False)


duplicate.short_description = "Duplicate selected items"


class VideoFileAdmin(TabbedTranslationAdmin):
    list_display = (
        "name",
        "item_type",
        "pk",
        "internal_name",
        "description",
        "author",
        "course",
        "section",
        "file",
        "thumbnail",
    )
    actions = [update_thumbnails, duplicate, refresh]
    list_filter = ("course",)
    save_as = True
    form = VideoFileAdminForm

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "description",
                    "content",
                    "author",
                    "course",
                    "section",
                    "start_date",
                    "end_date",
                    "show_related_content",
                    "published",
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
            "Video settings",
            {
                "fields": (
                    "file",
                    "internal_name",
                    "subtitle",
                    "thumbnail",
                )
            }
        )
    )


class PlaylistInline(SortableInlineAdminMixin, admin.TabularInline):
    model = VideoFile
    extra = 0


class PlaylistAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = (
        "name",
        "course",
    )
    inlines = (PlaylistInline,)


admin.site.register(VideoFile, VideoFileAdmin)
admin.site.register(Playlist, PlaylistAdmin)
