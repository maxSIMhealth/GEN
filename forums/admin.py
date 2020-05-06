from django.contrib import admin

from .models import MediaFile, Forum, Comment, VideoFile


def update_thumbnails(modeladmin, request, queryset):
    for item in queryset:
        item.generate_video_thumbnail()


update_thumbnails.short_description = "Update thumbnail of selected videos"


class CommentsAdmin(admin.ModelAdmin):
    # fields = ('author', 'message')
    # filter_horizontal = ('author', )
    list_display = ('author', 'message', 'forum')
    list_display_links = ('message', )
    list_filter = ('author', 'forum')


class VideoFileAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'author',
                    'course', 'file', 'thumbnail')
    actions = [update_thumbnails]


admin.site.register(MediaFile)
admin.site.register(VideoFile, VideoFileAdmin)
admin.site.register(Forum)
admin.site.register(Comment, CommentsAdmin)
