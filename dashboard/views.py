from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from courses.progress import progress


@login_required
def dashboard(request):
    user_progress = []

    for course in request.user.member.all():
        discussions = course.discussions.all()
        quizzes = course.quizzes.all()

        # progress status
        discussions_progress = progress(request, discussions)
        quizzes_progress = progress(request, quizzes)
        course_progress = {
            "name": course.code,
            "discussions": discussions_progress,
            "quizzes": quizzes_progress,
            "max": discussions_progress["max"] + quizzes_progress["max"],
        }
        user_progress.append(course_progress)

    return render(request, "dashboard.html", {"user_progress": user_progress})
