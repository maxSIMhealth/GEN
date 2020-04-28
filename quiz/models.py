from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from model_utils.models import TimeStampedModel
from model_utils.managers import InheritanceManager

from forums.models import Course, VideoFile


class Quiz(TimeStampedModel):
    """
    Quiz model
    """

    name = models.CharField(max_length=30, unique=True)
    description = models.CharField(max_length=100)
    author = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='quizzes')
    course = models.ForeignKey(
        Course, on_delete=models.PROTECT, related_name='quizzes')
    video = models.ForeignKey(
        VideoFile, on_delete=models.PROTECT, related_name='quizzes')

    class Meta:
        verbose_name_plural = "quizzes"

    def get_questions(self):
        return self.questions.all().select_subclasses()

    def __str__(self):
        return self.name


class Question(TimeStampedModel):
    """
    Question model
    Parent for Multiple Choice, Likert Scale and Open Ended questions
    """

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


class Likert(Question):
    """Likert Model"""

    def get_answers(self):
        return LikertAnswer.objects.filter(question=self)

    def __str__(self):
        return ("%s") % (self.content)

    class Meta:
        verbose_name = "Likert Scale Question"
        verbose_name_plural = "Likert Scale Questions"


class LikertAnswer(TimeStampedModel):
    """
    Likert answer (scale) model.
    Minimum and maximum values are used to generate the scale layout.
    """

    question = models.OneToOneField(Likert, on_delete=models.PROTECT)
    scale_min = models.PositiveIntegerField(default=1)
    scale_max = models.PositiveIntegerField(default=5)

    def __str__(self):
        return ("%s : scale %s to %s") % (self.question.content, self.scale_min, self.scale_max)

    def clean(self):
        # Don't allow max scale to be equal of lower than min scale
        if self.scale_max <= self.scale_min:
            raise ValidationError(
                'Maximum scale value cannot be equal or lower than minimum scale value.')
        return super().clean()

    class Meta:
        verbose_name = 'Likert Answer (scale)'
        verbose_name_plural = 'Likert Answers (scales)'


class LikertAttempt(TimeStampedModel):
    """
    Likert Attempt model
    """

    question = models.ForeignKey(Likert, on_delete=models.PROTECT)
    student = models.ForeignKey(User, on_delete=models.PROTECT)
    quiz = models.ForeignKey(Quiz, on_delete=models.PROTECT)
    course = models.ForeignKey(Course, on_delete=models.PROTECT)
    attempt_number = models.PositiveIntegerField(default=0)
    scale_answer = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        return "%s - %s - Course %s (attempt %s): %s" % \
            (self.student.get_full_name(),
             self.quiz.name,
             self.course.name,
             self.attempt_number,
             self.question)

    class Meta:
        verbose_name = "Likert Scale Attempt"
        verbose_name_plural = "Likert Scale Attempts"


class OpenEnded(Question):
    """
    Open Ended model
    """

    # def __str__(self):
    #     return ("%s") % (self.content)

    class Meta:
        verbose_name = "Open ended Question"
        verbose_name_plural = "Open ended questions"


class OpenEndedAttempt(TimeStampedModel):
    """
    Open Ended Attempt model
    """

    question = models.ForeignKey(OpenEnded, on_delete=models.PROTECT)
    student = models.ForeignKey(User, on_delete=models.PROTECT)
    quiz = models.ForeignKey(Quiz, on_delete=models.PROTECT)
    course = models.ForeignKey(Course, on_delete=models.PROTECT)
    answer = models.TextField(('answer'), null=True, blank=True)
    attempt_number = models.PositiveIntegerField(default=0)

    def __str__(self):
        return "%s - %s - Course %s (attempt %s): %s" % \
            (self.student.get_full_name(),
             self.quiz.name,
             self.course.name,
             self.attempt_number,
             self.question)

    class Meta:
        verbose_name = "Open Ended Attempt"
        verbose_name_plural = "Open Ended Attempts"


class MCQuestion(Question):
    def check_if_correct(self, guess):
        answer = MCAnswer.objects.get(id=guess)

        return bool(answer.correct)

    def get_answers(self):
        return MCAnswer.objects.filter(question=self)

    def get_answers_list(self):
        return [(answer.id, answer.content) for answer in
                MCAnswer.objects.filter(question=self)]

    class Meta:
        verbose_name = "Multiple Choice Question"
        verbose_name_plural = "Multiple Choice Questions"


class MCAnswer(TimeStampedModel):
    """
    Multiple choice question answer
    """

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

    class Meta:
        verbose_name = 'Multiple Choice Answer'
        verbose_name_plural = 'Multiple Choice Answers'


class MCQuestionAttempt(TimeStampedModel):
    student = models.ForeignKey(User, on_delete=models.PROTECT)
    quiz = models.ForeignKey(Quiz, on_delete=models.PROTECT)
    course = models.ForeignKey(Course, on_delete=models.PROTECT)
    question = models.ForeignKey(MCQuestion, on_delete=models.PROTECT)
    correct = models.NullBooleanField(blank=True, null=True)
    answer = models.ForeignKey(MCAnswer, on_delete=models.PROTECT)
    answer_content = models.CharField('student answer', max_length=1000)
    attempt_number = models.PositiveIntegerField(default=0)

    def __str__(self):
        return "Student %s - quiz %s - course %s (attempt %s): answer id %s" % \
            (self.student.get_full_name(),
             self.quiz.name,
             self.course.name,
             self.attempt_number,
             self.answer_id)

    class Meta:
        verbose_name = "Multiple Choice Questions Attempt"
        verbose_name_plural = "Multiple Choice Questions Attempts"


class QuizScore(models.Model):
    student = models.ForeignKey(User, on_delete=models.PROTECT)
    quiz = models.ForeignKey(Quiz, on_delete=models.PROTECT)
    course = models.ForeignKey(Course, on_delete=models.PROTECT)
    score = models.PositiveIntegerField(default=0)

    def __str__(self):
        return "Score for user %s - quiz %s - course %s" % \
            (self.student.username,
             self.quiz.name,
             self.course.name)
