from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import MCQuestion, MCQuestionAttempt, Quiz, Answer
from forums.models import Course


@login_required
def quiz(request, pk, quiz_pk):
    course = get_object_or_404(Course, pk=pk)
    quiz = get_object_or_404(Quiz, pk=quiz_pk)

    if request.method == 'POST':
        flag = False
        items = list(request.POST)
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

            attempt.save()

        return render(
            request,
            'quiz_result.html',
            {'course': course, "quiz": quiz})

    else:
        return render(
            request,
            'quiz.html',
            {'course': course, 'quiz': quiz})
