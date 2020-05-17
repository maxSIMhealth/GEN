from django import template

register = template.Library()


@register.simple_tag
def quiz_mcquestion_check(question, attempt_list):
    """
    Checks which Multiple Choice Question choice the user submitted
    """
    user_answers = []

    for attempt in attempt_list:
        if question.id == attempt.question_id:
            user_answers.append(attempt.answer_id)

    return user_answers
