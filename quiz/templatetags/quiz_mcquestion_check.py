from django import template

register = template.Library()


@register.simple_tag
def quiz_mcquestion_check(question, attempt_list):
    """
    Checks which Multiple Choice Question choice the user submitted
    """

    for attempt in attempt_list:
        if question.id == attempt.question_id:
            user_attempt = attempt.answer_id
        else:
            user_attempt = 0

    return user_attempt
