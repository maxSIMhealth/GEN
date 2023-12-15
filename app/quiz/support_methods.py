from GEN.support_methods import duplicate_object


def quiz_score_get(user, quiz):
    """
    Get user latest QuizScore for this quiz (if it exists).
    """
    from quiz.models import QuizScore

    latest_quizscore = None

    if quiz:
        try:
            latest_quizscore = quiz.quizscore_set.filter(
                student=user, quiz=quiz
            ).latest("attempt_number")
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
        requirement_fulfilled = bool(
            requirement_quiz_score and requirement_quiz_score.completed
        )

    else:
        requirement_fulfilled = True

    # check if submissions limit has been defined
    submissions_limit_reached = False
    if quiz.limit_submissions:
        submissions_max_number = quiz.limit_submissions_max
        if quiz.quizscore_set.count() >= submissions_max_number:
            submissions_limit_reached = True

    # check if quiz should be still available
    if not attempts_limit_reached and requirement_fulfilled and not submissions_limit_reached:
        quiz_enable = True

    return quiz_enable, current_attempt_number, attempts_left, latest_quizscore


def duplicate_quiz(quiz, course=None, section=None, suffix=None, **kwargs):
    """
    Duplicates a quiz and all related questions.
    Participants submissions WILL NOT be duplicated.

    :param quiz: Quiz object that will be duplicated.
    :param course: Optional: course object that the quiz will be related to.
    :param section: Optional: section object that the quiz will be related to.
    :param suffix: Optional: suffix string to be added to quiz name.
    :param kwargs: Optional: additional fields and values.
    :return: Quiz object.
    """

    original_quiz_pk = quiz.pk

    # duplicate quiz object
    if course is not None:
        quiz.course = course
    if section is not None:
        quiz.section = section
    duplicated_quiz = duplicate_object(quiz, suffix=suffix, **kwargs)

    # duplicate questions
    from quiz.models import Question

    questions = Question.objects.filter(quiz=original_quiz_pk)
    for question in questions:
        question.duplicate(quiz=duplicated_quiz)

    return duplicated_quiz


def duplicate_question(question, quiz=None, suffix=None):
    """
    Duplicates a quiz question.
    Participants submissions WILL NOT be duplicated.

    :param question: Question to be duplicated.
    :param quiz: Optional: quiz that will hold the question.
    :param suffix: suffix string to be added to quiz name.
    :return: Question object.
    """

    from quiz.models import LikertAnswer, MCAnswer

    original_question_pk = question.pk

    # get answers (if they exist) based on the type of question
    answers = None
    if question.question_type == "M":
        answers = MCAnswer.objects.filter(question=original_question_pk)
    elif question.question_type == "L":
        answers = LikertAnswer.objects.filter(question=original_question_pk)

    # set quiz that will hold the question
    if quiz is not None:
        question.quiz = quiz

    # duplicate question
    duplicated_question = duplicate_object(question, suffix=suffix)

    # duplicate answers (if they exist)
    if answers is not None:
        for answer in answers:
            duplicate_object(answer, question=duplicated_question)

    return duplicated_question
