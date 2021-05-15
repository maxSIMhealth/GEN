from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def dashboard(request):
    courses = request.user.member.all()

    return render(request, "dashboard.html", {
        "courses": courses,
    })
