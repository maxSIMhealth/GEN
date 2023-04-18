from courses.support_methods import progress, requirement_fulfilled

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import DashboardSetting


def check_items_requirement(user, items):
    for item in items:
        # only allow access to course if requirements have been fulfilled
        if item.requirement:
            item.requirement.fulfilled = requirement_fulfilled(user, item)


@login_required
def dashboard(request):
    user = request.user

    # get dashboard information, if any exists and is set as active
    try:
        dashboard_info = DashboardSetting.objects.filter(active=True)[0]
    except IndexError:
        dashboard_info = None

    # get courses that the user is a member of, and sort them by group
    courses_all = user.member.all().order_by("group", "custom_order")

    # add course progress information to course objects
    get_course_progress(user, courses_all)

    # check requirements
    check_items_requirement(user, courses_all)

    # check if course groups have all requirements fulfilled
    # groups_objects = Group.objects.filter(user=user)

    return render(
        request,
        "dashboard.html",
        {
            "dashboard_info": dashboard_info,
            "courses": courses_all,
            # "modules": modules
        },
    )


def get_course_progress(user, courses_queryset):
    for course_object in courses_queryset:
        sections = course_object.sections.filter(published=True)
        sections_progress = progress(user, course_object, sections)

        if sections_progress["current"] == sections_progress["max"]:
            course_object.progress = "completed"
        elif sections_progress["max"] > sections_progress["current"] > 0:
            course_object.progress = "started"
        else:
            course_object.progress = "not started"
