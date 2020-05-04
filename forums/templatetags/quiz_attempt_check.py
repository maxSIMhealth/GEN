from django import template
from quiz.models import QuestionAttempt

register = template.Library()


@register.simple_tag
def quiz_attempt_check(user, course, quiz):
    try:
        attempt_number = quiz.questionattempt_set.filter(
            student=user, course=course, quiz=quiz).latest('attempt_number').attempt_number
    except QuestionAttempt.DoesNotExist:
        attempt_number = 0
        print("No quiz attempt found")
    return attempt_number
