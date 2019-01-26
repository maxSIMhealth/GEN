from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from django.utils import timezone
from urllib.parse import urlparse

from .forms import NewForumForm, NewCommentForm, NewMediaForm
from .models import Course, Forum, Comment, MediaFile


def course(request, pk):
  course = get_object_or_404(Course, pk=pk)

  return render(request, 'course.html', {'course': course})

def course_forums(request, pk):
  course = get_object_or_404(Course, pk=pk)
  forums = course.forums.all()
  
  return render(request, 'course_forums.html', {'course': course, 'forums': forums})

def list_videos(request, pk):
  course = get_object_or_404(Course, pk=pk)
  forums = course.forums.all()

  return render(request, 'list_videos.html', {'course': course, 'forums': forums})

def list_pdfs(request, pk):
  course = get_object_or_404(Course, pk=pk)
  forums = course.forums.all()

  return render(request, 'list_pdfs.html', {'course': course, 'forums': forums})

def list_quiz(request, pk):
  course = get_object_or_404(Course, pk=pk)
  quizzes = course.quizzes.all()

  return render(request, 'list_quiz.html', {'course': course, 'quizzes': quizzes})

class ForumListView(ListView):
  # https://ccbv.co.uk/projects/Django/2.1/django.views.generic.list/ListView/
  # Render some list of objects, set by `self.model` or `self.queryset`.
  # `self.queryset` can actually be any iterable of items, not just a queryset.
  model = Forum
  context_object_name = 'forums'
  template_name = 'home.html'


def forum_comments(request, pk, forum_pk):
  course = get_object_or_404(Course, pk=pk)
  forum = get_object_or_404(Forum, pk=forum_pk)

  if request.method == 'POST':
    form = NewCommentForm(request.POST)
    if form.is_valid():
      forum.last_updated = timezone.now()
      forum.save()
      comment = Comment.objects.create(
        message = form.cleaned_data.get('message'),
        forum = forum,
        author = request.user
      )
      my_kwargs = dict(
        pk = course.pk,
        forum_pk = forum.pk
      )
      return redirect('forum_comments', **my_kwargs)
  else:
    form = NewCommentForm()

  return render(request, 'comments.html', {'forum': forum, 'course': course, 'form': form})


@login_required
def new_forum(request, pk):
  course = get_object_or_404(Course, pk=pk)
  forums = Forum.objects.all()

  if request.method == 'POST':
    form = NewForumForm(request.POST)
    media_form = NewMediaForm(request.POST)
    if form.is_valid() and media_form.is_valid() :
      media = MediaFile.objects.create(
        title = media_form.cleaned_data.get('title'),
        kind = media_form.cleaned_data.get('kind'),
        author = request.user,
        url = media_form.cleaned_data.get('url'),
      )
      forum = Forum.objects.create(
        course = course,
        name = form.cleaned_data.get('name'),
        description = form.cleaned_data.get('description'),
        media = media,
        author = request.user
      )
      
      return redirect('course_forums', pk=course.pk)
  else:
    form = NewForumForm()
    media_form = NewMediaForm()

  return render(request, 'new_forum.html', {'forums': forums, 'course': course, 'form': form, 'media_form': media_form})

def upvote_forum(request, pk, forum_pk):
  course = get_object_or_404(Course, pk=pk)
  forum = Forum.objects.get(pk=forum_pk)
  forum.votes.up(request.user.id)

  # checking if the user is voting from the forums list or from forum itself
  path = urlparse(request.META['HTTP_REFERER']).path + "upvote"

  my_kwargs = dict(
    pk = course.pk,
    forum_pk = forum.pk
  )

  if request.path == path:
    return redirect('forum_comments', **my_kwargs)
  else:
    return redirect('course_forums', pk=course.pk)

def clearvote_forum(request, pk, forum_pk):
  course = get_object_or_404(Course, pk=pk)
  forum = Forum.objects.get(pk=forum_pk)
  forum.votes.delete(request.user.id)

  # checking if the user is voting from the forums list or from forum itself
  path = urlparse(request.META['HTTP_REFERER']).path + "clearvote"

  my_kwargs = dict(
    pk = course.pk,
    forum_pk = forum.pk
  )

  if request.path == path:
    return redirect('forum_comments', **my_kwargs)
  else:
    return redirect('course_forums', pk=course.pk)

def upvote_comment(request, pk, forum_pk, comment_pk):
  comment = get_object_or_404(Comment, pk=comment_pk)
  comment.votes.up(request.user.id)

  my_kwargs = dict(
    pk = pk,
    forum_pk = forum_pk
  )

  return redirect('forum_comments', **my_kwargs)

def clearvote_comment(request, pk, forum_pk, comment_pk):
  comment = get_object_or_404(Comment, pk=comment_pk)
  comment.votes.delete(request.user.id)

  my_kwargs = dict(
    pk = pk,
    forum_pk = forum_pk
  )

  return redirect('forum_comments', **my_kwargs)