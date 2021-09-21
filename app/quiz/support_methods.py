def quiz_score_get(user, quiz):
    """
    Get user latest QuizScore for this quiz (if it exists).
    """
    from quiz.models import QuizScore
    try:
        latest_quizscore = (
            quiz.quizscore_set.filter(student=user, quiz=quiz)
                .latest("attempt_number")
        )
    except QuizScore.DoesNotExist:
        latest_quizscore = None
    return latest_quizscore


def quiz_enable_check(user, quiz):
    """
    Check if quiz should still be enabled for the user to answer
    """
    quiz_enable = False

    # get latest quiz score for user (if it exists)
    latest_quizscore = quiz_score_get(user, quiz)
    if latest_quizscore is not None:
        current_attempt_number = latest_quizscore.attempt_number
    else:
        current_attempt_number = 0

    # checks if the quiz allows multiple attempts
    if quiz.allow_multiple_attempts:
        attempts_max_number = quiz.attempts_max_number
    else:
        attempts_max_number = 1

    # check how many attempts are left
    attempts_left = attempts_max_number - current_attempt_number

    # check if user has reached the limit of attempts
    if attempts_left > 0:
        attempts_limit_reached = False
    else:
        attempts_limit_reached = True

    # check if quiz has a requirement
    if quiz.requirement:
        # get current attempt number for requirement
        requirement_quiz_score = quiz_score_get(user, quiz.requirement)

        # check if quiz requirement has been fulfilled
        requirement_fulfilled = bool(requirement_quiz_score.exists() and requirement_quiz_score.completed)

    else:
        requirement_fulfilled = True

    # check if quiz should be still available
    if not attempts_limit_reached and requirement_fulfilled:
        quiz_enable = True

    return quiz_enable, current_attempt_number, attempts_left, latest_quizscore


def duplicate_quiz(quiz, field=None, value=None):
    original_quiz_pk = quiz.pk

    # clone quiz object
    quiz.id = None
    quiz.pk = None
    quiz._state.adding = True
    if field is not None:
        setattr(quiz, field, value)
    quiz.save()

    # clone quiz questions
    from quiz.models import Question
    questions = Question.objects.filter(quiz=original_quiz_pk)

    for question in questions:
        from quiz.models import LikertAnswer, MCAnswer
        original_question_pk = question.pk
        answers = None
        if question.question_type == 'M':
            answers = MCAnswer.objects.filter(question=original_question_pk)
        elif question.question_type == 'L':
            answers = LikertAnswer.objects.filter(question=original_question_pk)
        question.id = None
        question.pk = None
        question.quiz = quiz
        question._state.adding = True
        question.save()

        if answers != None:
            for answer in answers:
                answer.id = None
                answer.pk = None
                answer._state.adding = True
                answer.question = question
                answer.save()

    return quiz
