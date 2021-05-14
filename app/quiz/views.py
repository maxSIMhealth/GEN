import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Max, Sum
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, reverse
from django.utils.translation import gettext_lazy as _
from GEN.decorators import course_enrollment_check
from GEN.support_methods import enrollment_test

# import xlsxwriter

from courses.models import Course, Section
from .models import (
    Likert,
    LikertAnswer,
    MCAnswer,
    MCQuestion,
    QuestionAttempt,
    Quiz,
    QuizScore,
    QUESTION_TYPES,
    MIN_PERCENTAGE,
    MAX_NUM_MISTAKES
)
from .support_methods import quiz_enable_check

# Get an instance of a logger
logger = logging.getLogger(__name__)


def question_likert_check(attempt, question, submitted_data):
    score = 0

    # try to get answer (scale) object
    try:
        likert = LikertAnswer.objects.get(question=question)
    except LikertAnswer.DoesNotExist:
        likert = None

    # get the likert scale value chosen by the participant
    try:
        student_answer = submitted_data[str(question.id)][0]
    except KeyError:
        student_answer = None

    if likert.check_answer:
        # check if the student answer is within expected range
        if student_answer:
            flag = Likert.check_if_correct(question, likert, int(student_answer))
            if flag is True:
                score += question.value
        else:
            flag = False
    else:
        # since there is no correct answer, we are marking the submission as correct and
        # adding the question value to the quiz score
        score += question.value
        flag = True

    # save participant answer attempt
    attempt.correct = flag
    attempt.answer_content = student_answer
    attempt.save()

    return score


def question_multiplechoice_check(attempt, question, submitted_data):
    score = 0
    flag = False

    # creating array of user submitted answers
    try:
        user_answers = submitted_data[str(question.id)]
    except KeyError:
        # since the user did not check any item,
        # creating an empty array
        user_answers = []

    if question.multiple_correct_answers:

        # checking each question answer item
        for answer in question.answers.all():
            # reset attempt object
            attempt.pk = None

            attempt.multiplechoice_answer = answer

            # verify if the answer was checked by the student
            answer_checked = str(answer.pk) in user_answers

            # check if the answer was marked correctly
            flag = answer.check == answer_checked

            if flag is True:
                score += 1

            attempt.answer_content = answer_checked
            attempt.correct = flag
            attempt.save()

    else:
        # checking user submitted answer
        for answer in user_answers:
            flag = MCQuestion.check_if_correct(question, answer)

            attempt.multiplechoice_answer = MCAnswer.objects.get(pk=answer)

            if flag is True:
                score += 1

        attempt.answer_content = attempt.multiplechoice_answer.content
        attempt.correct = flag
        attempt.save()

    return score


def question_check(attempt, question, submitted_data):

    if question.question_type == "L":
        score = question_likert_check(attempt, question, submitted_data)

    elif question.question_type == "M":
        score = question_multiplechoice_check(attempt, question, submitted_data)

    elif question.question_type == "O":
        # get the open ended answer
        student_answer = submitted_data[str(question.id)][0]
        # save participant answer attempt
        attempt.answer_content = student_answer
        attempt.save()
        score = 0
    else:
        score = 0

    return score


def quiz_submission(request, quiz, course, section):
    items = list(request.POST)
    attempt_number = QuestionAttempt.objects.filter(
        quiz=quiz, student=request.user
    ).aggregate(Max("attempt_number"))
    # removing csrf token from items list
    items.pop(0)
    score = 0
    # generating maximum score (removing Header and Open Ended items) at the time of submission
    max_score = quiz.questions.all().exclude(question_type='H').exclude(question_type='O').aggregate(Sum('value'))[
        'value__sum']
    # alternate query
    # max_score = Quiz.objects.filter(pk=quiz.pk).annotate(Sum('questions__value'))

    # increase attempt number
    if attempt_number["attempt_number__max"]:
        current_attempt_number = attempt_number["attempt_number__max"] + 1
    else:
        current_attempt_number = 1

    # get submitted questions and generate an dictionary list
    # format: {"question_id": "question_values"}
    submitted_data = dict()
    for item in items:
        try:
            temp, question_id = item.split("_")
            submitted_data[question_id] = request.POST.getlist(item)

        except IndexError:
            question_id = None

    # check if each question was answered by the participant
    for question in quiz.questions.all():
        # create new attempt object
        attempt = QuestionAttempt(
            student=request.user,
            quiz=quiz,
            course=course,
            section=section,
            question=question,
            question_type=question.question_type,
            attempt_number=current_attempt_number,
        )

        # add video name, if the quiz has a related video
        if quiz.video:
            attempt.video = quiz.video

        # check user submitted answers
        question_score = question_check(attempt, question, submitted_data)
        score += question_score

    # change session variable to indicate that the
    # user completed the quiz
    request.session["quiz_complete"] = True

    # check if user has quiz score
    if request.user.quizscore_set.filter(course=course, quiz=quiz).exists():
        # get student quiz score
        quiz_score = QuizScore.objects.get(
            student=request.user, course=course, quiz=quiz
        )
        # update score
        quiz_score.score = score
        quiz_score.max_score = max_score
        quiz_score.completed = False

    else:
        # create student quiz score
        quiz_score = QuizScore.objects.create(
            student=request.user, quiz=quiz, course=course, score=score, max_score=max_score
        )

    # save score data
    quiz_score.save()

    # perform quiz assessment (if enabled)
    quiz_score.perform_assessment()


@login_required
@course_enrollment_check(enrollment_test)
def quiz_page(request, pk, section_pk, quiz_pk):
    """
    Renders quiz page and handles submission requests
    """

    # get objects
    course = get_object_or_404(Course, pk=pk)
    section = get_object_or_404(Section, pk=section_pk)
    quiz = get_object_or_404(Quiz, pk=quiz_pk)

    # set session variable to indicate that the user has
    # not completed the quiz
    request.session["quiz_complete"] = False

    if quiz.published:

        # check if the quiz has a related video and if it has been published
        if quiz.video:
            if not quiz.video.published:
                raise Http404("The video this quiz is related to is not published.")
            else:
                pass

        # check if quiz has a requirement and if it should be enabled
        (quiz_enabled, temp) = quiz_enable_check(request.user, quiz)

        if quiz_enabled:

            if request.method == "POST":
                quiz_submission(request, quiz, course, section)

                # if flag:
                return HttpResponseRedirect(
                    reverse("quiz_result", args=[pk, section.pk, quiz.pk])
                )

            else:
                # get latest user attempt number (if it exists)
                try:
                    latest_attempt_number = (
                        QuestionAttempt.objects.filter(quiz=quiz, student=request.user)
                        .latest("attempt_number")
                        .attempt_number
                    )
                except QuestionAttempt.DoesNotExist:
                    latest_attempt_number = 0

                # check if user reached the maximum number of attempts
                # check if user has reached the limit of attempts
                if latest_attempt_number < quiz.attempts_max_number:
                    attempts_limit_reached = False
                else:
                    attempts_limit_reached = True

                # if the max number of attempts has been reached, redirect back to quiz list
                if attempts_limit_reached:
                    messages.error(
                        request,
                        _("You have already reached the maximum number of attempts."),
                    )
                    return HttpResponseRedirect(
                        reverse("section", args=[pk, section.pk])
                    )

                else:
                    return render(
                        request,
                        "quiz/quiz.html",
                        {"course": course, "section": section, "quiz": quiz},
                    )
        else:
            messages.error(
                request, _("Access denied."),
            )
            return HttpResponseRedirect(reverse("section", args=[pk, section.pk]))
    else:
        raise Http404("This quiz is not published.")


@login_required
@course_enrollment_check(enrollment_test)
def quiz_result(request, pk, section_pk, quiz_pk):
    # get objects
    course = get_object_or_404(Course, pk=pk)
    section = get_object_or_404(Section, pk=section_pk)
    quiz = get_object_or_404(Quiz, pk=quiz_pk)
    student_quiz_score = get_object_or_404(QuizScore, student=request.user, course=course, quiz=quiz)
    # score = student_quiz_score.score
    # max_score = student_quiz_score.max_score
    assessment_successful = None

    # check if the user is trying to directly access the result page
    # and redirects into que quiz list
    if request.session.get("quiz_complete") is False:
        return HttpResponseRedirect(reverse("section", args=[pk, section.pk]))

    # get latest attempt number
    latest_attempt_number = (
        QuestionAttempt.objects.filter(quiz=quiz, student=request.user)
        .latest("attempt_number")
        .attempt_number
    )

    # get questions and answers from the latest attempt
    try:
        questions_attempt = QuestionAttempt.objects.filter(
            quiz=quiz, student=request.user, attempt_number=latest_attempt_number
        )
    except QuestionAttempt.DoesNotExist:
        questions_attempt = []

    # split attempts into different categories
    attempt_likert = []
    attempt_mcquestion = []
    attempt_openended = []

    for item in questions_attempt:
        if item.question_type == "L":
            attempt_likert.append(item)
        elif item.question_type == "M":
            attempt_mcquestion.append(item)
        elif item.question_type == "O":
            attempt_openended.append(item)

    # reset the session variable
    request.session["quiz_complete"] = False

    # return render page
    return render(
        request,
        "quiz/quiz_result.html",
        {
            "course": course,
            "section": section,
            "quiz": quiz,
            "attempts": questions_attempt,
            "attempt_likert": attempt_likert,
            "attempt_mcquestion": attempt_mcquestion,
            "attempt_openended": attempt_openended,
            "user_quiz_score": student_quiz_score,
        },
    )


# FIXME: code below is WIP
# @login_required
# def user_attempt(request):
#     """
#     Create an excel file with Participant Attempts
#     """
#     # Create an in-memory output file for the new workbook
#     output = io.BytesIO()

#     # Creating workbook in memory
#     workbook = xlsxwriter.Workbook(output)

#     # Getting data
#     users = User.objects.all()
#     for user in users:
#         workbook = create_attempt_sheet(workbook, user)

#     # Close the workbook before sending the data
#     workbook.close()

#     # Rewind the buffer
#     output.seek(0)

#     # Set up the Http response
#     filename = "attempt.xlsx"
#     response = HttpResponse(
#         output,
#         content_type="application/vnd.openxmlformats-\
#                 officedocument.spreadsheetml.sheet",
#     )
#     response["Content-Disposition"] = "attachment; filename=%s" % filename

#     return response


# def create_attempt_sheet(workbook, user):
#     """
#     Create an excel sheet for Participant attempt
#     """
#     worksheet = workbook.add_worksheet(user.username)
#     bold = workbook.add_format({"bold": True})

#     # Write some data headers
#     worksheet.write("A1", "Test", bold)

#     return workbook
