from django.shortcuts import render, get_object_or_404, reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.db.models import Max

from .models import MCQuestion, MCQuestionAttempt, Quiz, Answer, QuizScore
from forums.models import Course


@login_required
def quiz(request, pk, quiz_pk):
    # get objects
    course = get_object_or_404(Course, pk=pk)
    quiz = get_object_or_404(Quiz, pk=quiz_pk)

    # set session variable to indicate that the user has
    # not completed the quiz
    request.session['quiz_complete'] = False

    if request.method == 'POST':
        flag = False
        items = list(request.POST)
        attempt_no = MCQuestionAttempt.objects.filter(
            quiz=quiz, student=request.user).aggregate(Max('attempt_no'))
        # removing csrf token from items list
        items.pop(0)
        score = 0

        # get each question id and get answer related to it
        for item in items:
            try:
                question_id = item.split('_')[1]
            except IndexError:
                question_id = None

            try:
                mcquestion = MCQuestion.objects.get(pk=question_id)
            except MCQuestion.DoesNotExist:
                mcquestion = None

            try:
                answer = Answer.objects.get(
                    pk=request.POST.getlist(item)[0])
            except IndexError:
                answer = None

            # check if the question is correct
            if MCQuestion.check_if_correct(mcquestion, answer.pk):
                flag = True
                score += 1

            # store the answers as a new attempt
            attempt = MCQuestionAttempt.objects.create(
                student=request.user,
                quiz=quiz,
                course=course,
                question=MCQuestion.objects.get(pk=question_id),
                correct=flag,
                # I've decided to save a pure text versio of the answer, in
                # case the answer object is altered in the future
                answer=answer.content
            )

            # increase attempt number
            if attempt_no['attempt_no__max']:
                attempt.attempt_no = attempt_no['attempt_no__max'] + 1
            else:
                attempt.attempt_no = 1

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
        return render(
            request,
            'quiz.html',
            {'course': course, 'quiz': quiz})


@login_required
def quiz_result(request, pk, quiz_pk):
    # get objects
    course = get_object_or_404(Course, pk=pk)
    quiz = get_object_or_404(Quiz, pk=quiz_pk)
    quiz_score_kwargs = dict(
        student=request.user,
        quiz=quiz,
        course=course
    )
    quiz_score = get_object_or_404(QuizScore, **quiz_score_kwargs)

    # check if the user is trying to directly access the result page
    # and redirects into que quiz list
    if request.session.get('quiz_complete') is False:
        return HttpResponseRedirect(reverse('list_quiz', args=[pk]))

    score = quiz_score.score

    # # get latest attempt number
    # attempt_no = MCQuestionAttempt.objects.filter(
    #     quiz=quiz, student=request.user).aggregate(Max('attempt_no'))

    # # get questions from the latest attemp
    # questions = MCQuestionAttempt.objects.filter(
    #     quiz=quiz,
    #     student=request.user,
    #     attempt_no=attempt_no['attempt_no__max']
    # )

    # # base score
    # score = 0

    # # increment score by 1 for each correct answer
    # for question in questions:
    #     if question.correct:
    #         score += 1

    # reset the session variable
    request.session['quiz_complete'] = False

    # return render page
    return render(request, 'quiz_result.html', {
        'course': course,
        'quiz': quiz,
        'score': score
    })
