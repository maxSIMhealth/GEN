from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from courses.support_methods import requirement_fulfilled
from courses.models import COURSE, MODULE


@login_required
def dashboard(request):
    user = request.user
    courses_all = user.member.all()

    for course in courses_all:
        # only allow access to course if requirements have been fulfilled
        if course.requirement:
            course.requirement.fulfilled = requirement_fulfilled(user, course)

    courses = courses_all.filter(type=COURSE)
    modules = courses_all.filter(type=MODULE)

    return render(request, "dashboard.html", {
        "courses": courses,
        "modules": modules
    })
