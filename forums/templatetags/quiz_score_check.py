from django import template

# from forums.models import Forum, Comment
# from quiz.models import QuizScore

register = template.Library()


@register.simple_tag
def quiz_score_check(user, course, quiz):
    return quiz.quizscore_set.filter(student=user, course=course, quiz=quiz)
