from django.db import models
from django.contrib.auth.models import User
from model_utils.models import TimeStampedModel
from model_utils.managers import InheritanceManager

from forums.models import Course, MediaFile


class Quiz(TimeStampedModel):
    name = models.CharField(max_length=30, unique=True)
    description = models.CharField(max_length=100)
    author = models.ForeignKey(User, on_delete=models.PROTECT, related_name='quizzes')
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name='quizzes')
    video = models.ForeignKey(MediaFile, on_delete=models.PROTECT, related_name='quizzes')

    class Meta:
        verbose_name_plural = "quizzes"

    def get_questions(self):
        return self.questions.all().select_subclasses()

    def __str__(self):
        return self.name


class Question(TimeStampedModel):
    quiz = models.ManyToManyField(
        Quiz,
        verbose_name='Quiz',
        related_name='questions',
        blank=True)
    # on_delete=models.PROTECT)
    content = models.CharField(
        max_length=1000,
        blank=False,
        help_text="Enter the question text that you want displayed ",
        verbose_name="Question")
    explanation = models.TextField(
        blank=True,
        help_text="Explanation to be shown after the question has been answered.")

    objects = InheritanceManager()

    def __str__(self):
        return self.content


class MCQuestion(Question):
    def check_if_correct(self, guess):
        answer = Answer.objects.get(id=guess)

        if answer.correct is True:
            return True
        else:
            return False

    def get_answers(self):
        return Answer.objects.filter(question=self)

    def get_answers_list(self):
        return [(answer.id, answer.content) for answer in Answer.objects.filter(question=self)]

    class Meta:
        verbose_name = "Multiple Choice Question"
        verbose_name_plural = "Multiple Choice Questions"


class Answer(models.Model):
    question = models.ForeignKey(
        MCQuestion,
        on_delete=models.CASCADE,
        related_name='answers'
    )

    content = models.CharField(
        max_length=1000,
        blank=False,
        help_text="Enter the answer text that you want displayed"
    )

    correct = models.BooleanField(
        blank=False,
        default=False,
        help_text="Is this the correct answer?"
    )

    def __str__(self):
        return self.content


class MCQuestionAttempt(TimeStampedModel):
    student = models.ForeignKey(User, on_delete=models.PROTECT)
    quiz = models.ForeignKey(Quiz, on_delete=models.PROTECT)
    course = models.ForeignKey(Course, on_delete=models.PROTECT)
    question = models.ForeignKey(MCQuestion, on_delete=models.PROTECT)
    correct = models.NullBooleanField(blank=True, null=True)
    answer = models.CharField('student answer', max_length=1000)
    attempt_no = models.PositiveIntegerField(default=0)

    def __str__(self):
        return "User %s - quiz %s - course %s - attempt %s" % (self.student.username, self.quiz.name, self.course.name, self.attempt_no)

    class Meta:
        verbose_name = "Multiple Choice Questions Attempt"
        verbose_name_plural = "Multiple Choice Questions Attempts"
