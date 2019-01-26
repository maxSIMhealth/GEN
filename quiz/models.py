from django.db import models
from django.contrib.auth.models import User
from model_utils.models import TimeStampedModel

from forums.models import Course, MediaFile

class Quiz(TimeStampedModel):
    name = models.CharField(max_length=30, unique=True)
    description = models.CharField(max_length=100)
    author = models.ForeignKey(User, on_delete=models.PROTECT, related_name='quizzes')
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name='quizzes')
    video = models.ForeignKey(MediaFile, on_delete=models.PROTECT, related_name='quizzes')

    class Meta:
        verbose_name_plural = "quizzes"

    def __str__(self):
        return self.name