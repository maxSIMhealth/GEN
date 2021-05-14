from django import template

from quiz.support_methods import quiz_enable_check, quiz_score_get

register = template.Library()


class QuizDetails:
    def __init__(self, enabled, current_attempt_number, attempts_left, scoreset):
        self.enabled = enabled
        self.current_attempt_number = current_attempt_number
        self.attempts_left = attempts_left
        self.scoreset = scoreset


@register.simple_tag
def quiz_details_get(user, quiz):
    enabled, current_attempt_number, attempts_left = quiz_enable_check(user, quiz)
    scoreset = quiz_score_get(user, quiz)

    return QuizDetails(enabled, current_attempt_number, attempts_left, scoreset)
