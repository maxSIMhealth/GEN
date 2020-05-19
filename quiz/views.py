import io

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Max
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, reverse
import xlsxwriter

from forums.models import Course
from .models import (
    Likert,
    LikertAnswer,
    LikertAttempt,
    MCAnswer,
    MCQuestion,
    MCQuestionAttempt,
    OpenEnded,
    OpenEndedAttempt,
    QuestionAttempt,
    Quiz,
    QuizScore,
)
from .support_methods import quiz_enable_check


# FIXME: split quiz_page into multiple methods
@login_required
def quiz_page(request, pk, quiz_pk):
    """
    Renders quiz page and handles submission requests
    """

    # get objects
    course = get_object_or_404(Course, pk=pk)
    quiz = get_object_or_404(Quiz, pk=quiz_pk)

    # set session variable to indicate that the user has
    # not completed the quiz
    request.session["quiz_complete"] = False

    if quiz.published:

        # check if quiz has a requirement and if it should be enabled
        (quiz_enabled, _) = quiz_enable_check(request.user, quiz)

        if quiz_enabled:

            if request.method == "POST":
                flag = False
                items = list(request.POST)
                attempt_number = MCQuestionAttempt.objects.filter(
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

                # get each question id and get answer related to it
                for item in items:
                    try:
                        question_type, question_id = item.split("_")
                    except IndexError:
                        question_id = None

                    if question_type == "mcquestion":
                        try:
                            mcquestion = MCQuestion.objects.get(pk=question_id)
                        except MCQuestion.DoesNotExist:
                            mcquestion = None

                        try:
                            user_answers = MCAnswer.objects.filter(
                                id__in=request.POST.getlist(item)
                            )
                        except IndexError:
                            user_answers = None

                        # check if the answer is correct
                        for answer in user_answers:
                            if MCQuestion.check_if_correct(mcquestion, answer.pk):
                                # FIXME: consider changing flag to consider
                                # partially correct answers
                                flag = True
                                score += 1
                            else:
                                flag = False

                            # store the answers as a new attempt
                            attempt = MCQuestionAttempt.objects.create(
                                student=request.user,
                                quiz=quiz,
                                course=course,
                                question=MCQuestion.objects.get(pk=question_id),
                                correct=flag,
                                # I've decided to save a pure text version of the answer, in
                                # case the answer object is altered in the future
                                answer_content=answer.content,
                                answer=MCAnswer.objects.get(pk=answer.pk),
                                attempt_number=current_attempt_number,
                            )

                            # save attempt data
                            attempt.save()

                    elif question_type == "openended":
                        try:
                            question = OpenEnded.objects.get(pk=question_id)
                        except OpenEnded.DoesNotExist:
                            question = None

                        student_answer = request.POST.get(item)

                        # store answers
                        attempt = OpenEndedAttempt.objects.create(
                            student=request.user,
                            quiz=quiz,
                            course=course,
                            question=question,
                            answer_content=student_answer,
                            attempt_number=current_attempt_number,
                        )

                        # save attempt data
                        attempt.save()

                    elif question_type == "likert":
                        try:
                            question = Likert.objects.get(pk=question_id)
                        except Likert.DoesNotExist:
                            question = None

                        # try to get answer (scale) object
                        try:
                            scale = LikertAnswer.objects.get(question=question)
                        except LikertAnswer.DoesNotExist:
                            scale = None

                        # get the likert scale value chosen by the participant
                        student_answer = request.POST.get(item)

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

                        # create new attempt
                        attempt = LikertAttempt.objects.create(
                            student=request.user,
                            quiz=quiz,
                            course=course,
                            question=question,
                            attempt_number=current_attempt_number,
                        )

                        # check if the submitted answer is valid (integer)
                        try:
                            attempt.answer_content = student_answer
                            attempt.save()
                        except ValueError:
                            attempt.answer_content = None

                        # save attempt data
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
                return HttpResponseRedirect(reverse("quiz_result", args=[pk, quiz.pk]))

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
                    return HttpResponseRedirect(reverse("list_quiz", args=[pk]))

                else:
                    return render(
                        request, "quiz.html", {"course": course, "quiz": quiz}
                    )
        else:
            raise Http404("You do not fulfill the requirements to access this page.")
    else:
        raise Http404("Quiz does not exist.")


@login_required
def quiz_result(request, pk, quiz_pk):
    # get objects
    course = get_object_or_404(Course, pk=pk)
    quiz = get_object_or_404(Quiz, pk=quiz_pk)
    # get quiz score object
    quiz_score_kwargs = dict(student=request.user, quiz=quiz, course=course)
    score = get_object_or_404(QuizScore, **quiz_score_kwargs).score

    # check if the user is trying to directly access the result page
    # and redirects into que quiz list
    if request.session.get("quiz_complete") is False:
        return HttpResponseRedirect(reverse("list_quiz", args=[pk]))

    # get latest attempt number
    latest_attempt_number = (
        QuestionAttempt.objects.filter(quiz=quiz, student=request.user)
        .latest("attempt_number")
        .attempt_number
    )

    # get questions and answers from the latest attempt
    questions_attempt = QuestionAttempt.objects.filter(
        quiz=quiz, student=request.user, attempt_number=latest_attempt_number
    )

    # split attempts into different categories
    attempt_likert = []
    attempt_mcquestion = []
    attempt_openended = []

    for item in questions_attempt:
        if hasattr(item, "likertattempt"):
            attempt_likert.append(item.likertattempt)
        elif hasattr(item, "mcquestionattempt"):
            attempt_mcquestion.append(item.mcquestionattempt)
        elif hasattr(item, "openendedattempt"):
            attempt_openended.append(item.openendedattempt)

    # reset the session variable
    request.session["quiz_complete"] = False

    # return render page
    return render(
        request,
        "quiz_result.html",
        {
            "course": course,
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


@login_required
def list_quiz(request, pk):
    course = get_object_or_404(Course, pk=pk)
    quizzes = course.quizzes.all().filter(published=True)

    return render(request, "list_quiz.html", {"course": course, "quizzes": quizzes})


def create_attempt_sheet(workbook, user):
    """
    Create an excel sheet for Participant attempt
    """
    worksheet = workbook.add_worksheet(user.username)
    bold = workbook.add_format({"bold": True})

    # Write some data headers
    worksheet.write("A1", "Test", bold)

    return workbook
