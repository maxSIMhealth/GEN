from quiz.models import QuestionAttempt


def quiz_attempts_get(user, quiz):
    """
    Get user current attempt number for this quiz
    """
    try:
        current_attempt_number = (
            quiz.questionattempt_set.filter(student=user, quiz=quiz)
            .latest("attempt_number")
            .attempt_number
        )
    except QuestionAttempt.DoesNotExist:
        # if there are no questionAttempt objects it means that the user
        # never answered this quiz
        current_attempt_number = 0
    return current_attempt_number


def quiz_score_get(user, quiz):
    return quiz.quizscore_set.filter(student=user, quiz=quiz)


def quiz_enable_check(user, quiz):
    """
    Check if quiz should still be enabled for the user to answer
    """
    attempts_limit_reached = False
    requirement_fulfilled = False
    quiz_enable = False
    attempts_max_number = 0

    # get current attempt number
    current_attempt_number = quiz_attempts_get(user, quiz)

    # checks if the quiz allows multiple attempts
    if quiz.allow_multiple_attempts:
        attempts_max_number = quiz.attempts_max_number
    else:
        attempts_max_number = 1

    # check if user has reached the limit of attempts
    if current_attempt_number < attempts_max_number:
        attempts_limit_reached = False
    else:
        attempts_limit_reached = True

    # check if quiz has a requirement
    if quiz.requirement:
        # get current attempt number for requirement
        requirement_quiz_score = quiz_score_get(user, quiz.requirement)

        # check if quiz requirement has been fulfilled
        requirement_fulfilled = bool(requirement_quiz_score.exists())

    else:
        requirement_fulfilled = True

    # check if quiz should be still available
    if not attempts_limit_reached and requirement_fulfilled:
        quiz_enable = True

    return (quiz_enable, current_attempt_number)
