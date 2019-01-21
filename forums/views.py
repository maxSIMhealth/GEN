from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.forms import inlineformset_factory
from django.views.generic import ListView
from .forms import NewForumForm, NewCommentForm
from .models import Forum, Comment


class ForumListView(ListView):
  # https://ccbv.co.uk/projects/Django/2.1/django.views.generic.list/ListView/
  # Render some list of objects, set by `self.model` or `self.queryset`.
  # `self.queryset` can actually be any iterable of items, not just a queryset.
  model = Forum
  context_object_name = 'forums'
  template_name = 'home.html'


def forum_comments(request, pk):
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

  return render(request, 'comments.html', {'forum': forum, 'form': form})


@login_required
def new_forum(request):
  forums = Forum.objects.all()
  user = User.objects.first()

  if request.method == 'POST':
    form = NewForumForm(request.POST)
    if form.is_valid():
      forum = Forum.objects.create(
        name = form.cleaned_data.get('name'),
        description = form.cleaned_data.get('description'),
        kind = form.cleaned_data.get('kind'),
        url = form.cleaned_data.get('url'),
        author = user
      )
      return redirect('home')
  else:
    form = NewForumForm()

  return render(request, 'new_forum.html', {'forums': forums, 'form': form})