import logging
import random

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, reverse
from django.utils.functional import cached_property
from django_tables2 import SingleTableView
from django_tables2.export.views import ExportMixin

from GEN.decorators import course_enrollment_check, check_permission
from GEN.support_methods import enrollment_test
from core.mixins import BlockPeersAccessMixin
from core.support_methods import check_is_instructor
from courses.models import Course, Section
from courses.support_methods import mark_section_completed, review_course_status
from .models import (
    Likert,
    LikertAnswer,
    MCAnswer,
    MCQuestion,
    QuestionAttempt,
    Quiz,
    QuizScore,
    Question
)
from .support_methods import quiz_enable_check
from .tables import QuestionAttemptTable

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

            multiplechoice_answers_correct = []

            # checking each question answer item
            for answer in question.answers.all():
                # reset attempt object
                attempt.pk = None

                attempt.multiplechoice_answer = answer

                # verify if the answer was checked by the student
                answer_checked = str(answer.pk) in user_answers

                # check if the answer was marked correctly
                flag = answer.check == answer_checked

                # TODO: implement partial score for each correct item

                attempt.answer_content = answer_checked
                attempt.correct = flag
                attempt.save()

                multiplechoice_answers_correct.append(flag)

            if all(multiplechoice_answers_correct):
                score += question.value

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


def quiz_submission(request, quiz, questions, course, section):
    items = list(request.POST)
    # removing csrf token from items list
    items.pop(0)
    score = 0
    num_mistakes = 0
    max_score = 0
    try:
        latest_attempt_number = QuizScore.objects.filter(
            student=request.user,
            course=course,
            quiz=quiz) \
            .latest('attempt_number').attempt_number
    except QuizScore.DoesNotExist:
        latest_attempt_number = 0

    user_scoreset = QuizScore(
        student=request.user,
        course=course,
        quiz=quiz,
        max_mistakes=quiz.assessment_max_mistakes,
        min_percentage=quiz.assessment_min_percentage,
        attempt_number=latest_attempt_number
    )

    # sets if quiz is submitted by an expert/instructor
    user_scoreset.expert_feedback = check_is_instructor(course, request.user)

    # increase attempt number
    user_scoreset.attempt_number = user_scoreset.attempt_number + 1
    user_scoreset.save()

    # get submitted questions and generate an dictionary list
    # format: {"question_id": "question_values"}
    submitted_data = dict()
    for item in items:
        temp, question_id = item.split("_")
        submitted_data[question_id] = request.POST.getlist(item)

    # check if each question was answered by the participant
    for question in questions:
        # create new attempt object
        attempt = QuestionAttempt(
            student=request.user,
            quiz=quiz,
            quiz_score=user_scoreset,
            course=course,
            section=section,
            question=question,
            question_type=question.question_type,
            attempt_number=user_scoreset.attempt_number,
        )

        # add question value to max score
        max_score += question.value

        # add video name, if the quiz has a related video
        if quiz.video:
            attempt.video = quiz.video

        # check user submitted answers
        question_score = question_check(attempt, question, submitted_data)
        score += question_score

        # increase mistake counter if attempt is incorrect
        if attempt.correct is False and (question.question_type != 'H' or question.question_type != 'O'):
            num_mistakes += 1

    # change session variable to indicate that the
    # user completed the quiz
    request.session["quiz_complete"] = True

    # update scoreset
    user_scoreset.score = score
    user_scoreset.num_mistakes = num_mistakes

    # setting max score at the time of submission (just in case the quiz is modified later)
    user_scoreset.max_score = max_score

    # check if the quiz has been completed successfully (this method does not perform a save)
    user_scoreset.perform_assessment()

    # save updated user scoreset
    user_scoreset.save()

    quiz_evaluate_completion(request, section)


def quiz_evaluate_completion(request, section):
    # get all section quiz scores, excluding ones that the user is the author/owner
    # check if all are marked as completed
    # if yes, mark section as completed
    section_quizzes = section.section_items.exclude(author=request.user)
    # completed = passed assessment (if assessment method is enabled)
    section_quizzes_completed = []

    for quiz in section_quizzes:
        try:
            quizscore = QuizScore.objects.filter(quiz=quiz, student=request.user).latest("attempt_number")
        except QuizScore.DoesNotExist:
            quizscore = None
        if quizscore:
            section_quizzes_completed.append(quizscore.completed)
        else:
            section_quizzes_completed.append(False)

    if all(section_quizzes_completed):
        # if the quiz section is a pre-assessment section, and the learner succeeds in the quizzes, mark the
        # whole course (all sections) as completed - it basically allows the learner to skip the course content
        # while a final assessment (in theory) is the last section of the course
        if section.pre_assessment or section.final_assessment:
            review_course_status(request, section.course, force=True)
        else:
            mark_section_completed(request, section)
    else:
        if section.pre_assessment:
            # for pre-assessment, the section should be marked completed even if the learner 'fails' the quiz
            mark_section_completed(request, section)


@login_required
@course_enrollment_check(enrollment_test)
@check_permission("quiz")
def quiz_page(request, pk, section_pk, sectionitem_pk):
    """
    Renders quiz page and handles submission requests
    """

    # get objects
    course = get_object_or_404(Course, pk=pk)
    section = get_object_or_404(Section, pk=section_pk)
    quiz = get_object_or_404(Quiz, pk=sectionitem_pk)

    if quiz.published:
        # check if the quiz has a related video and if it has been published
        if quiz.video and not quiz.video.published:
            raise Http404("The video this quiz is related to is not published.")
        else:
            pass

        # check if quiz has a requirement and if it should be enabled
        (quiz_enabled, _, attempts_left, _) = quiz_enable_check(request.user, quiz)

        if quiz_enabled:
            if request.method == "POST":
                # block quiz author from submitting on own quiz
                if quiz.author == request.user:
                    messages.error(
                        request, _("Submission denied. You can not submit a quiz of which you are the author."),
                    )
                    return HttpResponseRedirect(
                        reverse("section", args=[pk, section.pk])
                    )

                questions_ids = request.session["quiz_questions"]
                questions = quiz.questions.filter(pk__in=questions_ids)
                quiz_submission(request, quiz, questions, course, section)

                # if flag:
                return HttpResponseRedirect(
                    reverse("quiz_result", args=[pk, section.pk, quiz.pk])
                )

            else:
                # check if randomization is enabled and use subset number
                if quiz.randomize:
                    questions = list(quiz.questions.all())
                    subset_number = quiz.subset_number if quiz.subset else questions.__len__()
                    questions = random.sample(questions, subset_number)
                else:
                    questions = quiz.questions.all()

                # set session variable to indicate that the user has
                # not completed the quiz
                request.session["quiz_complete"] = False

                # set session variable with questions ids (necessary to correctly identify which questions are being
                # used in case of randomization)
                questions_ids = []
                for question in questions:
                    questions_ids.append(question.pk)
                request.session["quiz_questions"] = questions_ids

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
                        {"course": course, "section": section, "quiz": quiz, "questions": questions},
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
def quiz_result(request, pk, section_pk, sectionitem_pk):
    # get objects
    course = get_object_or_404(Course, pk=pk)
    section = get_object_or_404(Section, pk=section_pk)
    quiz = get_object_or_404(Quiz, pk=sectionitem_pk)
    student_quiz_score = QuizScore.objects.filter(student=request.user, course=course, quiz=quiz) \
        .latest("attempt_number")

    # check if the user is trying to directly access the result page
    # and redirects into que quiz list
    if request.session.get("quiz_complete") is False:
        return HttpResponseRedirect(reverse("section", args=[pk, section.pk]))

    # get latest attempt number
    latest_attempt_number = student_quiz_score.attempt_number

    # get questions and answers from the latest attempt
    try:
        questions_attempt = student_quiz_score.questionattempt_set.filter(
            quiz=quiz,
            attempt_number=latest_attempt_number
        )
        # merging multiple choice attempts of a same question
        # questions_attempt_distinct = questions_attempt.distinct("question")

        # working but not showing correct answer status (it might show 'correct' for an 'incorrect' answer)
        # questions_attempt_distinct = questions_attempt.distinct('created', 'question')

        # getting multiple choice attempts of the same question, removing dupes from initial queryset and
        # re-adding distinct question attempt to queryset
        # FIXME: this is UGLY, there has to be a better way
        from django.db.models import Count
        dupes_list = questions_attempt.values('question').annotate(Count('id')).order_by().filter(id__count__gt=1)
        dupes = questions_attempt.filter(question__in=[item['question'] for item in dupes_list])
        dupes_incorrect = dupes.filter(correct=False).distinct('created', 'question')
        dupes_correct = dupes.filter(correct=True).distinct('created', 'question')
        questions_attempt_distinct = questions_attempt.difference(dupes)
        if dupes_incorrect:
            questions_attempt_distinct = questions_attempt_distinct.union(dupes_incorrect)
        else:
            questions_attempt_distinct = questions_attempt_distinct.union(dupes_correct)

    except QuestionAttempt.DoesNotExist:
        questions_attempt_distinct = None
        questions_attempt = []

    questions = Question.objects.filter(quiz=quiz, id__in=questions_attempt.values('question'))

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

    # check pre and final assessments
    assessment_status = None
    if section.pre_assessment or section.final_assessment:
        # query used to obtain list QuizScores that are part of the current section,
        # and them get their 'completed' values as a list
        quiz_count = section.section_items.count()
        quiz_scores = QuizScore.objects.filter(student=request.user,
                                               quiz__in=section.section_items.values('pk')).values_list('completed',
                                                                                                        flat=True)

        if len(quiz_scores) == quiz_count:
            if all(quiz_scores):
                assessment_status = 'Complete'
            else:
                assessment_status = 'Failed'
        elif len(quiz_scores) < quiz_count:
            assessment_status = 'Incomplete'

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
            "questions": questions,
            "attempts": questions_attempt_distinct,
            "attempt_likert": attempt_likert,
            "attempt_mcquestion": attempt_mcquestion,
            "attempt_openended": attempt_openended,
            "user_quiz_score": student_quiz_score,
            "assessment_status": assessment_status
        },
    )


class QuestionAttemptListView(LoginRequiredMixin, BlockPeersAccessMixin, ExportMixin, SingleTableView):
    model = QuestionAttempt
    table_class = QuestionAttemptTable
    template_name = 'quiz/quiz_result_list.html'

    @cached_property
    def quiz_data(self, **kwargs):
        quiz_pk = self.kwargs['sectionitem_pk']
        quiz_data = QuestionAttempt.objects.filter(quiz=quiz_pk)
        quiz_data_users = quiz_data.order_by('student').distinct('student').values_list('student', flat=True)
        return quiz_data, quiz_data_users

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add additional objects to context based on url kwargs
        course_pk = context['view'].kwargs['pk']
        section_pk = context['view'].kwargs['section_pk']
        quiz_pk = context['view'].kwargs['sectionitem_pk']
        context['course'] = get_object_or_404(Course, pk=course_pk)
        context['section'] = get_object_or_404(Section, pk=section_pk)
        context['quiz'] = get_object_or_404(Quiz, pk=quiz_pk)
        _, context['results_list'] = self.quiz_data
        return context

    def get_queryset(self, **kwargs):
        quiz_data, quiz_data_users = self.quiz_data
        if 'student' in self.request.GET:
            item_id = int(self.request.GET['student'])
        else:
            item_id = False
        if item_id:
            queryset = quiz_data.filter(student=item_id)
        else:
            if quiz_data_users:
                queryset = quiz_data.filter(student=quiz_data_users[0])
            else:
                queryset = quiz_data
        return queryset
