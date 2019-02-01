from django.shortcuts import render, get_object_or_404, reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.db.models import Max

from .models import MCQuestion, MCQuestionAttempt, Quiz, Answer
from forums.models import Course


@login_required
def quiz(request, pk, quiz_pk):
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

        for item in items:
            try:
                # question_id = key.split('_')[1]
                question_id = item.split('_')[1]
            except:
                question_id = None

            try:
                mcquestion = MCQuestion.objects.get(pk=question_id)
            except MCQuestion.DoesNotExist:
                mcquestion = None

            try:
                answer = Answer.objects.get(
                    content=request.POST.getlist(item)[0])
            except:
                answer = None

            if MCQuestion.check_if_correct(mcquestion, answer.pk):
                flag = True

            attempt = MCQuestionAttempt.objects.create(
                student=request.user,
                quiz=Quiz.objects.get(pk=quiz.pk),
                course=Course.objects.get(pk=course.pk),
                question=MCQuestion.objects.get(pk=question_id),
                # I've decided to save a pure text versio of the answer, in
                # case the answer object is altered in the future
                answer=answer.content,
                correct=flag
            )

            attempt.attempt_no = attempt_no['attempt_no__max'] + 1

            # if attempt_no['attempt_no__max']:
            #     attempt.attempt_no = attempt_no['attempt_no__max'] + 1

            attempt.save()

            # change session variable to indicate that the
            # user completed the quiz
            request.session['quiz_complete'] = True

        # if flag:
        return HttpResponseRedirect(reverse('quiz_result', args=[pk, quiz.pk]))
            # return redirect('quiz_result', pk=pk, quiz_pk=quiz.pk)

        # return render(
        #     request,
        #     'quiz_result.html',
        #     {'course': course, "quiz": quiz})

        # return redirect('quiz_result')

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

    # check if the user is trying to directly access the result page
    # and redirects into que quiz list
    if request.session.get('quiz_complete') is False:
        return HttpResponseRedirect(reverse('list_quiz', args=[pk]))

    # get latest attempt number
    attempt_no = MCQuestionAttempt.objects.filter(
        quiz=quiz, student=request.user).aggregate(Max('attempt_no'))

    # get questions from the latest attemp
    questions = MCQuestionAttempt.objects.filter(
        quiz=quiz,
        student=request.user,
        attempt_no=attempt_no['attempt_no__max']
    )

    # base score
    score = 0

    # increment score by 1 for each correct answer
    for question in questions:
        if question.correct:
            score += 1

    # reset the session variable
    request.session['quiz_complete'] = False

    # return render page
    return render(request, 'quiz_result.html', {
        'course': course,
        'quiz': quiz
    })
