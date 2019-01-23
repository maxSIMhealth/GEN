from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
  return render(request, 'dashboard.html')