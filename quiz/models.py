from django.db import models
from django.contrib.auth.models import User

from forums.models import Course

class Quiz(models.Model):
  course = models.ForeignKey(Course)
  author = models.ForeignKey(User)

  name = models.CharField(max_length=30, unique=True)
  description = models.CharField(max_length=100)

  def __str__(self):
      return self.name