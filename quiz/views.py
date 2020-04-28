from django.shortcuts import render, get_object_or_404, reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.db.models import Max

from forums.models import Course
from .models import MCQuestion, MCQuestionAttempt, Quiz, Answer, QuizScore,\
    Likert, LikertAnswer, LikertAttempt, OpenEnded, OpenEndedAttempt


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
    request.session['quiz_complete'] = False

    if request.method == 'POST':
        flag = False
        items = list(request.POST)
        attempt_number = MCQuestionAttempt.objects.filter(
            quiz=quiz, student=request.user).aggregate(Max('attempt_number'))
        # removing csrf token from items list
        items.pop(0)
        score = 0

        # get each question id and get answer related to it
        for item in items:
            try:
                question_type, question_id = item.split('_')
            except IndexError:
                question_id = None

            if question_type == 'mcquestion':
                try:
                    mcquestion = MCQuestion.objects.get(pk=question_id)
                except MCQuestion.DoesNotExist:
                    mcquestion = None

                try:
                    answer = Answer.objects.get(
                        pk=request.POST.get(item))
                except IndexError:
                    answer = None

                # check if the answer is correct
                if MCQuestion.check_if_correct(mcquestion, answer.pk):
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
                    answer=Answer.objects.get(pk=answer.pk)
                )

                # increase attempt number
                if attempt_number['attempt_number__max']:
                    attempt.attempt_number = attempt_number['attempt_number__max'] + 1
                else:
                    attempt.attempt_number = 1

                # save attempt data
                attempt.save()

            elif question_type == 'openended':
                try:
                    openended = OpenEnded.objects.get(pk=question_id)
                except OpenEnded.DoesNotExist:
                    openended = None

                value = request.POST.get(item)

                # store answers
                attempt = OpenEndedAttempt.objects.create(
                    openended=openended,
                    student=request.user,
                    answer=value
                )

                # increase attempt number
                if attempt_number['attempt_number__max']:
                    attempt.attempt_number = attempt_number['attempt_number__max'] + 1
                else:
                    attempt.attempt_number = 1

                # save attempt data
                attempt.save()

            elif question_type == 'likert':
                try:
                    likert = Likert.objects.get(pk=question_id)
                except Likert.DoesNotExist:
                    likert = None

                # check if the answer is valid
                try:
                    answer = LikertAnswer.objects.get(question=likert)
                except LikertAnswer.DoesNotExist:
                    answer = None
                # FIXME: disabled because it does not make sense to check
                # if a likert answer is correct or not
                # if answer:
                #     flag = True
                #     score += 1
                # else:
                #     flag = False

                # get the likert scale value chosen by the participant
                value = request.POST.get(item)

                # store the answer as a new attempt
                attempt = LikertAttempt.objects.create(
                    likert=likert,
                    student=request.user,
                    scale_answer=value
                )

                # increase attempt number
                if attempt_number['attempt_number__max']:
                    attempt.attempt_number = attempt_number['attempt_number__max'] + 1
                else:
                    attempt.attempt_number = 1

                # save attempt data
                attempt.save()

        # change session variable to indicate that the
        # user completed the quiz
        request.session['quiz_complete'] = True

        # check if user has quiz score
        if request.user.quizscore_set.filter(course=course, quiz=quiz).exists():
            # get student quiz score
            quiz_score = QuizScore.objects.get(
                student=request.user,
                course=course,
                quiz=quiz
            )
            # update score
            quiz_score.score = score

        else:
            # create student quiz score
            quiz_score = QuizScore.objects.create(
                student=request.user,
                quiz=quiz,
                course=course,
                score=score
            )

        # save score data
        quiz_score.save()

        # if flag:
        return HttpResponseRedirect(reverse('quiz_result', args=[pk, quiz.pk]))

    else:
        # mcquestions = MCQuestion.objects.filter(
        #     quiz=quiz)  # .order_by("-date_added")
        # likert = Likert.objects.filter(quiz=quiz)  # .order_by("-date_added")
        # openended = OpenEnded.objects.filter(quiz=quiz)

        return render(
            request,
            'quiz.html',
            {'course': course, 'quiz': quiz})


@login_required
def quiz_result(request, pk, quiz_pk):
    # get objects
    course = get_object_or_404(Course, pk=pk)
    quiz = get_object_or_404(Quiz, pk=quiz_pk)
    # quiz_score_kquiz_score_kwargs = dict(
    #     student=request.user,
    #     quiz=quiz,
    #     course=course
    # )
    # quiz_score = get_object_or_404(QuizScore, **quiz_score_kwargs)

    # check if the user is trying to directly access the result page
    # and redirects into que quiz list
    if request.session.get('quiz_complete') is False:
        return HttpResponseRedirect(reverse('list_quiz', args=[pk]))

    # score = quiz_score.score

    # get latest attempt number
    latest_attempt_number = MCQuestionAttempt.objects.filter(
        quiz=quiz, student=request.user).latest('attempt_number').attempt_number

    # get questions and answers from the latest attemp
    questions_attempt = MCQuestionAttempt.objects.filter(
        quiz=quiz,
        student=request.user,
        attempt_number=latest_attempt_number
    )

    # base score
    score = 0

    # increment score by 1 for each correct answer
    for question in questions_attempt:
        if question.correct:
            score += 1

    # reset the session variable
    request.session['quiz_complete'] = False

    # return render page
    return render(request, 'quiz_result.html', {
        'course': course,
        'quiz': quiz,
        'score': score
    })
