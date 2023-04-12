from courses.support_methods import requirement_fulfilled

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

    # get courses that the user is a member of, and sort them by group
    courses_all = user.member.all().order_by("group", "custom_order")

    # get dashboard information, if any exists and is set as active
    try:
        dashboard_info = DashboardSetting.objects.filter(active=True)[0]
    except IndexError:
        dashboard_info = None

    # check requirements
    check_items_requirement(user, courses_all)
    # check_items_requirement(user, modules)

    return render(
        request,
        "dashboard.html",
        {
            "dashboard_info": dashboard_info,
            "courses": courses_all,
            # "modules": modules
        },
    )
