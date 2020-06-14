import io
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Max
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, reverse
import xlsxwriter

from courses.models import Course, Section
from .models import (
    LikertAnswer,
    MCAnswer,
    MCQuestion,
    QuestionAttempt,
    Quiz,
    QuizScore,
)
from .support_methods import quiz_enable_check

# Get an instance of a logger
logger = logging.getLogger(__name__)


# FIXME: split quiz_page into multiple methods
@login_required
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
        (quiz_enabled, _) = quiz_enable_check(request.user, quiz)

        if quiz_enabled:

            if request.method == "POST":
                flag = False
                items = list(request.POST)
                attempt_number = QuestionAttempt.objects.filter(
                    quiz=quiz, student=request.user
                ).aggregate(Max("attempt_number"))
                # removing csrf token from items list
                items.pop(0)
                score = 0

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
                        _, question_id = item.split("_")
                        submitted_data[question_id] = request.POST.getlist(item)

                    except IndexError:
                        question_id = None

                # check if each question was answered by the participant
                for question in quiz.questions.all():
                    # create new attempt object
                    attempt = QuestionAttempt.objects.create(
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

                    # check if the participant answered the question
                    if submitted_data.get(str(question.id)):
                        logger.info("Question answer found")
                        if question.question_type == "L":
                            # try to get answer (scale) object
                            try:
                                scale = LikertAnswer.objects.get(question=question)
                            except LikertAnswer.DoesNotExist:
                                scale = None

                            # get the likert scale value chosen by the participant
                            student_answer = submitted_data[str(question.id)][0]

                            # check if the student answer is within defined scale
                            # INFO: decided to not change student answer and treat it on the
                            # generated report afterwards
                            if (
                                not scale.scale_min
                                <= int(student_answer)
                                <= scale.scale_max
                            ):
                                # student_answer = None
                                pass
                        elif question.question_type == "M":
                            # try to get multiple choice answers objects
                            try:
                                user_answers = MCAnswer.objects.filter(
                                    id__in=submitted_data[str(question.id)]
                                )
                            except IndexError:
                                user_answers = None

                            # save user_answers to attempt object
                            attempt.multiplechoice_answers.set(user_answers)

                            # check if the answer is correct
                            flag_mcquestion = []
                            student_answer = []

                            for answer in user_answers:
                                if MCQuestion.check_if_correct(question, answer.pk):
                                    flag_mcquestion.append(True)
                                    score += 1
                                else:
                                    flag_mcquestion.append(False)

                                student_answer.append(answer.content)

                            # FIXME: consider changing flag to consider partially
                            # correct answers (for questions with multiple answers)
                            if flag_mcquestion.__contains__(False):
                                flag = False
                            else:
                                flag = True

                            # set field based on if the answer was correct or not
                            attempt.correct = flag

                        elif question.question_type == "O":
                            # get the open ended answer
                            student_answer = submitted_data[str(question.id)][0]

                        # save participant answer attempt
                        attempt.answer_content = student_answer
                        attempt.save()
                    else:
                        # save attempt with empty 'answer_content',
                        # since the participant didn't answer it
                        logger.info("Question answer **NOT** found")
                        attempt.correct = False
                        attempt.save()

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

                else:
                    # create student quiz score
                    quiz_score = QuizScore.objects.create(
                        student=request.user, quiz=quiz, course=course, score=score
                    )

                # save score data
                quiz_score.save()

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
                    # FIXME: show a message stating that the user has reached the
                    # maximum number of attempts
                    messages.error(
                        request,
                        "You have already reached the maximum number of attempts.",
                    )
                    return HttpResponseRedirect(
                        reverse("section", args=[pk, section.pk])
                    )

                else:
                    return render(
                        request,
                        "quiz.html",
                        {"course": course, "section": section, "quiz": quiz},
                    )
        else:
            messages.error(
                request, "Access denied.",
            )
            return HttpResponseRedirect(reverse("section", args=[pk, section.pk]))
    else:
        raise Http404("This quiz is not published.")


@login_required
def quiz_result(request, pk, section_pk, quiz_pk):
    # get objects
    course = get_object_or_404(Course, pk=pk)
    section = get_object_or_404(Section, pk=section_pk)
    quiz = get_object_or_404(Quiz, pk=quiz_pk)
    # get quiz score object
    quiz_score_kwargs = dict(student=request.user, quiz=quiz, course=course)
    score = get_object_or_404(QuizScore, **quiz_score_kwargs).score

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
        "quiz_result.html",
        {
            "course": course,
            "section": section,
            "quiz": quiz,
            "attempt_likert": attempt_likert,
            "attempt_mcquestion": attempt_mcquestion,
            "attempt_openended": attempt_openended,
            "score": score,
        },
    )


@login_required
def user_attempt(request):
    """
    Create an excel file with Participant Attempts
    """
    # Create an in-memory output file for the new workbook
    output = io.BytesIO()

    # Creating workbook in memory
    workbook = xlsxwriter.Workbook(output)

    # Getting data
    users = User.objects.all()
    for user in users:
        workbook = create_attempt_sheet(workbook, user)

    # Close the workbook before sending the data
    workbook.close()

    # Rewind the buffer
    output.seek(0)

    # Set up the Http response
    filename = "attempt.xlsx"
    response = HttpResponse(
        output,
        content_type="application/vnd.openxmlformats-\
                officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = "attachment; filename=%s" % filename

    return response


def create_attempt_sheet(workbook, user):
    """
    Create an excel sheet for Participant attempt
    """
    worksheet = workbook.add_worksheet(user.username)
    bold = workbook.add_format({"bold": True})

    # Write some data headers
    worksheet.write("A1", "Test", bold)

    return workbook
