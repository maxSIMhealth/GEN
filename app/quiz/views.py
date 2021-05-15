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
from courses.support_methods import section_mark_completed
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

    if user_answers:
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
                    score += question.value

                attempt.answer_content = answer_checked
                attempt.correct = flag
                attempt.save()

        else:
            # checking user submitted answer
            for answer in user_answers:
                flag = MCQuestion.check_if_correct(question, answer)

                attempt.multiplechoice_answer = MCAnswer.objects.get(pk=answer)

                if flag is True:
                    score += question.value

            attempt.answer_content = attempt.multiplechoice_answer.content
    else:
        attempt.answer_content = None

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
    # removing csrf token from items list
    items.pop(0)
    score = 0
    num_mistakes = 0

    # try to get user quiz scoreset, create if it does not exist
    try:
        user_scoreset = QuizScore.objects.get(
            student=request.user,
            course=course,
            quiz=quiz
        )
    except:
        user_scoreset = QuizScore(
            student=request.user,
            quiz=quiz,
            course=course,
            max_score=quiz.max_score,
        )

    # increase attempt number if prior attempt exists
    user_scoreset.attempt_number = user_scoreset.attempt_number + 1

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
            attempt_number=user_scoreset.attempt_number,
        )

        # add video name, if the quiz has a related video
        if quiz.video:
            attempt.video = quiz.video

        # check user submitted answers
        question_score = question_check(attempt, question, submitted_data)
        score += question_score

        # increase mistake counter if attempt is incorrect
        if attempt.correct == False and (question.question_type != 'H' or question.question_type != 'O'):
            num_mistakes = user_scoreset.num_mistakes + 1

    # change session variable to indicate that the
    # user completed the quiz
    request.session["quiz_complete"] = True

    # update scoreset
    user_scoreset.score = score
    user_scoreset.num_mistakes = num_mistakes

    # setting max score at the time of submission (just in case the quiz is modified later)
    user_scoreset.max_score = quiz.max_score

    # check if the quiz has been completed successfully (this method does not perform a save)
    user_scoreset.perform_assessment()

    # save updated user scoreset
    user_scoreset.save()

    quiz_evaluate_completion(request, section)


def quiz_evaluate_completion(request, section):
    # get all section quiz scores
    # check if all are marked as completed
    # if yes, mark section as completed

    section_quizzes = section.section_items.all()
    section_quizzes_completed = []
    section_completed = False

    for quiz in section_quizzes:
        try:
            quizscore = QuizScore.objects.get(quiz=quiz,student=request.user)
        except:
            quizscore = None
        if quizscore:
            section_quizzes_completed.append(quizscore.completed)
        else:
            section_quizzes_completed.append(False)

    if all(section_quizzes_completed):
        section_mark_completed(request, section)

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
        (quiz_enabled, current_attempt_number, attempts_left) = quiz_enable_check(request.user, quiz)

        if quiz_enabled:

            if request.method == "POST":
                quiz_submission(request, quiz, course, section)

                # if flag:
                return HttpResponseRedirect(
                    reverse("quiz_result", args=[pk, section.pk, quiz.pk])
                )

            else:
                # if the max number of attempts has been reached, redirect back to quiz list
                if attempts_left <= 0:
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
