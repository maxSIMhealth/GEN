from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.forms import inlineformset_factory
from .forms import NewForumForm, NewMediaForm, NewCommentForm
from .models import Forum, Comment, Media


def home(request):
  forums = Forum.objects.all()
  return render(request, 'home.html', {'forums': forums})


def forum_comments(request, pk):
  forum = get_object_or_404(Forum, pk=pk)
  media = Media.objects.get(forum=forum)
  return render(request, 'comments.html', {'forum': forum, 'media': media})


# def new_comment(request, pk):
#   forum = get_object_or_404(Forum, pk=pk)
#   return render(request, 'new_comment.html', {'forum': forum})


def new_forum(request):
  forums = Forum.objects.all()
  user = User.objects.first()

  ForumFormSet = inlineformset_factory(Forum, Media, form=NewForumForm, extra=1)

  if request.method == 'POST':
    form = NewForumForm(request.POST)
    # form = ForumFormSet(request.POST)
    if form.is_valid():
      forum = Forum.objects.create(
        name = form.cleaned_data.get('name'),
        description = form.cleaned_data.get('description'),
        author = user
      )
      # form.save()
      return redirect('home')
  else:
    form = NewForumForm()
    # form = ForumFormSet()

  return render(request, 'new_forum.html', {'forums': forums, 'form': form})


def new_media(request, pk):
  forum = get_object_or_404(Forum, pk=pk)
  user = User.objects.first()

  if request.method == 'POST':
    form = NewMediaForm(request.POST)
    if form.is_valid():
      media = Media.objects.create(
        url = form.cleaned_data.get('url'),
        # kind = kind
        description = form.cleaned_data.get('description'),
        author = user,
        forum = forum
      )
      return redirect('forum_comments', pk=forum.pk)
  else:
    form = NewMediaForm()
  
  return render(request, 'new_media.html', {'forum': forum, 'form': form}) 


def new_comment(request, pk):
  forum = get_object_or_404(Forum, pk=pk)
  user = User.objects.first()

  if request.method == 'POST':
    form = NewCommentForm(request.POST)
    if form.is_valid():
      comment = Comment.objects.create(
        message = form.cleaned_data.get('message'),
        forum = forum,
        author = user
      )
      return redirect('forum_comments', pk=forum.pk)
  else:
    form = NewCommentForm()

  return render(request, 'new_comment.html', {'forum': forum, 'form': form})