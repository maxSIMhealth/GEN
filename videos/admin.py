from django.contrib import admin

from .models import VideoFile


def update_thumbnails(modeladmin, request, queryset):
    for item in queryset:
        item.generate_video_thumbnail()


update_thumbnails.short_description = "Update thumbnail of selected videos"


class VideoFileAdmin(admin.ModelAdmin):
    list_display = ("title", "description", "author", "course", "file", "thumbnail")
    actions = [update_thumbnails]


admin.site.register(VideoFile, VideoFileAdmin)
