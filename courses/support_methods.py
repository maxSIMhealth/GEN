from quiz.support_methods import quiz_score_get


def requirement_fulfilled(user, section):
    requirement = section.requirement

    fulfilled = False
    if requirement.section_type == "Q":
        # check if all quizzes have been answered
        quizzes_answered = []
        for item in requirement.section_items.all():
            quizzes_answered.append(quiz_score_get(user, item.quiz).exists())
        fulfilled = all(element for element in quizzes_answered)

    return fulfilled
