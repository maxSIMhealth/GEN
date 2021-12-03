from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import DashboardSettings

from courses.support_methods import requirement_fulfilled
from courses.models import COURSE, MODULE

@login_required
def dashboard(request):
    user = request.user
    courses_all = user.member.all()

    # get dashboard information, if any exists and is set as active
    try:
        dashboard_info = DashboardSettings.objects.filter(active=True)[0]
    except IndexError:
        dashboard_info = None

    for course in courses_all:
        # only allow access to course if requirements have been fulfilled
        if course.requirement:
            course.requirement.fulfilled = requirement_fulfilled(user, course)

    courses = courses_all.filter(type=COURSE)
    modules = courses_all.filter(type=MODULE)

    return render(request, "dashboard.html", {
        "dashboard_info": dashboard_info,
        "courses": courses,
        "modules": modules
    })
