from django.db import models
from django.contrib.auth.models import User
from vote.models import VoteModel

class Forum(VoteModel, models.Model):
    YOUTUBE = 'YTB'
    PDF = 'PDF'

    ATTACHMENT_KINDS = [
        (PDF, 'PDF Document'),
        (YOUTUBE, 'Youtube Video'),
    ]

    name = models.CharField(max_length=30, unique=True)
    description = models.CharField(max_length=100)
    author = models.ForeignKey(User, on_delete=models.PROTECT, related_name='forums')
    last_updated = models.DateTimeField(auto_now_add=True)
    kind = models.CharField(
        max_length=3,
        choices=ATTACHMENT_KINDS,
        default=YOUTUBE
    )
    url = models.URLField(max_length=200)

    def __str__(self):
        return self.name

    def get_comment_count(self):
        return Forum.objects.filter(comments__forum=self).count()


class Comment(models.Model):
    message = models.TextField(max_length=400)
    forum = models.ForeignKey(Forum, on_delete=models.CASCADE, related_name='comments')
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')

    def __str__(self):
        return self.message
    