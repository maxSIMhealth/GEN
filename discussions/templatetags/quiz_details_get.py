from django import template

from quiz.support_methods import quiz_enable_check, quiz_score_get

register = template.Library()


class QuizDetails:
    def __init__(self, enabled, attempts, score):
        self.enabled = enabled
        self.attempts = attempts
        self.score = score


@register.simple_tag
def quiz_details_get(user, quiz):
    enabled, attempts = quiz_enable_check(user, quiz)
    score = quiz_score_get(user, quiz)

    return QuizDetails(enabled, attempts, score)
