from django.shortcuts import render, get_object_or_404
from .models import Forum

def home(request):
  forums = Forum.objects.all()
  return render(request, 'home.html', {'forums': forums})

def forum_comments(request, pk):
  forum = get_object_or_404(Forum, pk=pk)
  return render(request, 'comments.html', {'forum': forum})