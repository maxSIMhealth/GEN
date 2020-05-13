from django.db import models
from django.contrib.auth.models import User


class Course(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField('course code', max_length=10)
    description = models.CharField(max_length=400)
    author = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='course')
    start_date = models.DateTimeField('start date', blank=True, null=True)
    end_date = models.DateTimeField('end date', blank=True, null=True)
    students = models.ManyToManyField(User, related_name='member')
    instructors = models.ManyToManyField(User, related_name='instructor')
    enable_gamification = models.BooleanField(default=True)
    show_scoreboard = models.BooleanField(default=True)
    show_leaderboard = models.BooleanField(default=True)
    show_progress_tracker = models.BooleanField(default=True)

    def __str__(self):
        return self.name
