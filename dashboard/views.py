from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from forums.models import Course
from forums.progress import progress


@login_required
def dashboard(request):
    user_progress = []

    for course in request.user.member.all():
        forums = course.forums.all()
        quizzes = course.quizzes.all()

        # progress status
        forums_progress = progress(request, forums)
        quizzes_progress = progress(request, quizzes)
        course_progress = {
            'name': course.code,
            'forums': forums_progress,
            'quizzes': quizzes_progress,
            'max': forums_progress['max'] + quizzes_progress['max']
        }
        # course_progress = [forums_progress, quizzes_progress]
        user_progress.append(course_progress)


    # courses = Course.objects.filter()
    # forums = course.forums.all()
    # quizzes = course.quizzes.all()

    # progress status
    # forums_progress = progress(request, forums)
    # quizzes_progress = progress(request, quizzes)

    return render(request, 'dashboard.html', {'user_progress': user_progress})
