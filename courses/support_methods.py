from discussions.support_methods import has_participated
from quiz.support_methods import quiz_score_get


def requirement_fulfilled(user, section):
    """
    Check if all section requirements have been fulfilled
    """
    requirement = section.requirement

    fulfilled = False
    items_completed = []

    for item in requirement.section_items.all():
        if requirement.section_type == "Q":
            items_completed.append(quiz_score_get(user, item.quiz).exists())
        elif requirement.section_type == "D":
            items_completed.append(has_participated(user, item.discussion))
        elif requirement.section_type == "U":
            if requirement.section_items.count() > 0:
                items_completed.append(True)
        elif requirement.section_type == "V":
            if item.videofile.quizzes.exists():
                for quiz in item.videofile.quizzes.all():
                    items_completed.append(quiz_score_get(user, quiz).exists())

        fulfilled = all(element for element in items_completed)

    return fulfilled
