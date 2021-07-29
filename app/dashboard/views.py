from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from core.views import check_is_instructor
from courses.support_methods import requirement_fulfilled


@login_required
def dashboard(request):
    user = request.user
    courses = user.member.all()

    for course in courses:
        # only allow access to course if requirements have been fulfilled
        if course.requirement:
            course.requirement.fulfilled = requirement_fulfilled(user, course)

    return render(request, "dashboard.html", {
        "courses": courses,
    })
