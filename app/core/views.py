from core.models import HelpFaq

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

# FIXME: this is a DEBUG ONLY function
from django.utils.decorators import method_decorator
from django.views.generic import ListView


@login_required
def reset(request):
    user = request.user
    is_instructor = bool(user.instructor.all())

    if not is_instructor:
        section_items = user.section_items.all()  # for video items
        quiz_scores = user.quizscore_set.all()
        quiz_attempts_answers = user.questionattempt_set.all()
        discussion_comments = user.comments.all()
        statuses = user.status.all()

        user_objects = [
            section_items,
            quiz_scores,
            quiz_attempts_answers,
            discussion_comments,
            statuses,
        ]

        for element in user_objects:
            for item in element:
                item.delete()

    return redirect("home")


@method_decorator(login_required, name="dispatch")
class HelpPageView(ListView):

    model = HelpFaq
    template_name = "help/help.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
