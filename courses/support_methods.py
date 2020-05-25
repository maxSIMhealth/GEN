from discussions.support_methods import has_participated
from quiz.support_methods import quiz_score_get


def requirement_fulfilled(user, section):
    """
    Check if all section requirements have been fulfilled
    """
    requirement = section.requirement

    fulfilled = False
    items_completed = []
    # check if user is a course instructor or system staff
    is_instructor = bool(section.course in user.instructor.all())
    if is_instructor or user.is_staff:
        fulfilled = True
    else:
        for item in requirement.section_items.all():
            if requirement.section_type == "Q":
                items_completed.append(quiz_score_get(user, item.quiz).exists())
            elif requirement.section_type == "D":
                items_completed.append(has_participated(user, item.discussion))
            elif requirement.section_type == "U":
                item_uploaded = (
                    requirement.section_items.all()
                    .filter(author=user, published=True)
                    .count()
                    > 0
                )
                items_completed.append(item_uploaded)
            elif requirement.section_type == "V":
                if item.videofile.quizzes.exists():
                    for quiz in item.videofile.quizzes.all():
                        items_completed.append(quiz_score_get(user, quiz).exists())
            else:
                items_completed.append(False)

            fulfilled = all(element for element in items_completed)

    return fulfilled
