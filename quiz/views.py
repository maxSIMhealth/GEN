from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from .models import MCQuestion, MCQuestionAttempt, Quiz
from forums.models import Course, MediaFile


def quiz(request, pk, quiz_pk):
  course = get_object_or_404(Course, pk=pk)
  quiz = get_object_or_404(Quiz, pk=quiz_pk)

  return render(request, 'quiz.html', {'course': course, 'quiz': quiz})