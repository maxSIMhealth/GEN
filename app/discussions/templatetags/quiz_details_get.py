from quiz.support_methods import quiz_enable_check

from django import template

register = template.Library()


class QuizDetails:
    def __init__(
        self, enabled, current_attempt_number, attempts_left, latest_quizscore
    ):
        self.enabled = enabled
        self.current_attempt_number = current_attempt_number
        self.attempts_left = attempts_left
        self.latest_quizscore = latest_quizscore


@register.simple_tag
def quiz_details_get(user, quiz):
    (
        enabled,
        current_attempt_number,
        attempts_left,
        latest_quizscore,
    ) = quiz_enable_check(user, quiz)

    return QuizDetails(enabled, current_attempt_number, attempts_left, latest_quizscore)
