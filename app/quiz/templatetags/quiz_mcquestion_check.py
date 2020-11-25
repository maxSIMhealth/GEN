from django import template

register = template.Library()


@register.simple_tag
def quiz_mcquestion_check(question, attempt_list):
    """
    Checks which Multiple Choice Question choice the user submitted
    """
    user_answers = dict()

    for attempt in attempt_list:
        if question.id == attempt.question_id:
            user_answers[attempt.multiplechoice_answer.id] = attempt.correct
            # user_answers.append(attempt.multiplechoice_answer.id)
            # for answer in attempt.multiplechoice_answers.all():
            #     user_answers.append(answer.id)

    return user_answers
