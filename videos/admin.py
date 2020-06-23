from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin
from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from .forms import VideoFileAdminForm
from .models import Playlist, VideoFile


def update_thumbnails(modeladmin, request, queryset):
    for item in queryset:
        item.generate_video_thumbnail()


update_thumbnails.short_description = "Update thumbnail of selected videos"


class VideoFileAdmin(TranslationAdmin):
    list_display = (
        "name",
        "internal_name",
        "description",
        "author",
        "course",
        "section",
        "file",
        "thumbnail",
    )
    actions = [update_thumbnails]
    list_filter = ("course",)
    save_as = True
    form = VideoFileAdminForm


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
