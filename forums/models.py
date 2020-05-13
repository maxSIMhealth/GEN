from django.db import models
from django.contrib.auth.models import User

from vote.models import VoteModel
from courses.models import Course
from videos.models import VideoFile


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'user_{0}/{1}'.format(instance.author.id, filename)


class MediaFile(models.Model):
    # FIXME: this should be renamed to DocumentFile or something like that

    YOUTUBE = 'YTB'
    PDF = 'PDF'

    ATTACHMENT_KINDS = [
        (PDF, 'PDF Document'),
        (YOUTUBE, 'Youtube Video'),
    ]

    title = models.CharField(max_length=100, unique=True)
    kind = models.CharField(
        max_length=3,
        choices=ATTACHMENT_KINDS,
        default=YOUTUBE
    )
    author = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='medias')
    url = models.URLField(max_length=200)

    def __str__(self):
        return self.title


class Forum(VoteModel, models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.PROTECT, related_name='forums')
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=400)
    author = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='forums')
    last_updated = models.DateTimeField(auto_now_add=True)
    # FIXME: media should be renamed to document or something like that
    # media = models.ForeignKey(
    #     MediaFile, on_delete=models.CASCADE, related_name='forums')
    video = models.ForeignKey(
        VideoFile, on_delete=models.CASCADE, related_name='forums', blank=True, null=True)

    def __str__(self):
        return self.name

    def get_comment_count(self):
        return Forum.objects.filter(comments__forum=self).count()


class Comment(VoteModel, models.Model):
    message = models.TextField(max_length=400)
    forum = models.ForeignKey(
        Forum, on_delete=models.CASCADE, related_name='comments')
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments')

    def __str__(self):
        return self.message
