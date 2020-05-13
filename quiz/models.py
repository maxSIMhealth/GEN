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

    name = models.CharField(max_length=30, unique=False)
    description = models.CharField(max_length=100)
    author = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='quizzes')
    course = models.ForeignKey(
        Course,
        on_delete=models.PROTECT,
        related_name='quizzes')
    start_date = models.DateTimeField('start date', blank=True, null=True)
    end_date = models.DateTimeField('end date', blank=True, null=True)
    video = models.ForeignKey(
        VideoFile,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name='quizzes')
    requirement = models.ForeignKey(
        'self',
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name='quizzes'
    )
    attempts_max_number = models.PositiveIntegerField(
        default=1,
        blank=False,
        null=False
    )
    published = models.BooleanField(default=False)
    custom_order = models.PositiveIntegerField(
        default=0,
        blank=False,
        null=False
    )

    class Meta:
        verbose_name_plural = "quizzes"
        ordering = ['custom_order']

    def get_questions(self):
        return self.questions.all().select_subclasses()

    def __str__(self):
        return self.name


class Question(TimeStampedModel):
    """
    Parent class for questions (Multiple Choice, Likert Scale and Open Ended)
    and for question headers.
    """

    quiz = models.ForeignKey(
        Quiz,
        verbose_name='Quiz',
        related_name='questions',
        blank=False,
        on_delete=models.PROTECT)
    content = models.CharField(
        max_length=1000,
        blank=False,
        help_text="Enter the content that you want displayed.",
        verbose_name="Content")
    explanation = models.TextField(
        blank=True,
        help_text="Explanation to be shown after the question has been answered.")
    custom_order = models.PositiveIntegerField(
        default=0,
        blank=False,
        null=False
    )

    objects = InheritanceManager()

    class Meta:
        ordering = ['custom_order']

    def __str__(self):
        return self.content


class QuestionAttempt(TimeStampedModel):
    student = models.ForeignKey(User, on_delete=models.PROTECT)
    quiz = models.ForeignKey(Quiz, on_delete=models.PROTECT)
    course = models.ForeignKey(Course, on_delete=models.PROTECT)
    attempt_number = models.PositiveIntegerField(default=0)

    objects = InheritanceManager()

    class Meta:
        verbose_name = "Question attempt"
        verbose_name_plural = "Question attempts"


class Likert(Question):
    """Likert Model"""

    def get_answers(self):
        return LikertAnswer.objects.filter(question=self)

    def __str__(self):
        return ("%s") % (self.content)

    class Meta:
        verbose_name = "Likert question"
        verbose_name_plural = "Likert questions"


class LikertAnswer(TimeStampedModel):
    """
    Likert answer (scale) model.
    Minimum and maximum values are used to generate the scale layout.
    """

    question = models.OneToOneField(Likert, on_delete=models.CASCADE)
    scale_min = models.PositiveIntegerField(default=1)
    scale_max = models.PositiveIntegerField(default=5)
    legend = models.TextField(
        blank=True,
        help_text="Legend for the likert scale values.")

    def __str__(self):
        return ("%s : scale %s to %s") % (self.question.content, self.scale_min, self.scale_max)

    def clean(self):
        # Don't allow max scale to be equal of lower than min scale
        if self.scale_max <= self.scale_min:
            raise ValidationError(
                'Maximum scale value cannot be equal or lower than minimum scale value.')
        return super().clean()

    class Meta:
        verbose_name = 'Likert answer (scale definition)'
        verbose_name_plural = 'Likert answers (scale definition)'


class LikertAttempt(QuestionAttempt):
    """
    Likert Attempt model
    """

    question = models.ForeignKey(Likert, on_delete=models.PROTECT)
    answer_content = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        return "%s - %s - Course %s (attempt %s): %s" % \
            (self.student.get_full_name(),
             self.quiz.name,
             self.course.name,
             self.attempt_number,
             self.question)

    class Meta:
        verbose_name = "Likert attempt"
        verbose_name_plural = "Likert attempts"


class OpenEnded(Question):
    """
    Open Ended model
    """

    # def __str__(self):
    #     return ("%s") % (self.content)

    class Meta:
        verbose_name = "Open ended question"
        verbose_name_plural = "Open ended questions"


class OpenEndedAttempt(QuestionAttempt):
    """
    Open Ended Attempt model
    """

    question = models.ForeignKey(OpenEnded, on_delete=models.PROTECT)
    answer_content = models.TextField(('answer'), null=True, blank=True)

    def __str__(self):
        return "%s - %s - Course %s (attempt %s): %s" % \
            (self.student.get_full_name(),
             self.quiz.name,
             self.course.name,
             self.attempt_number,
             self.question)

    class Meta:
        verbose_name = "Open ended attempt"
        verbose_name_plural = "Open ended attempts"


class MCQuestion(Question):
    multiple_correct_answers = models.BooleanField(
        blank=False,
        default=False,
        help_text="Does this question have multiple correct answers \
            (allow user to select multiple answer items)?"
    )

    def check_if_correct(self, guess):
        answer = MCAnswer.objects.get(id=guess)

        return bool(answer.correct)

    def get_answers(self):
        return MCAnswer.objects.filter(question=self)

    def get_answers_list(self):
        return [(answer.id, answer.content) for answer in
                MCAnswer.objects.filter(question=self)]

    class Meta:
        verbose_name = "Multiple choice question"
        verbose_name_plural = "Multiple choice questions"


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

    custom_order = models.PositiveIntegerField(
        default=0,
        blank=False,
        null=False
    )

    def __str__(self):
        return self.content

    class Meta:
        verbose_name = 'Multiple choice answer'
        verbose_name_plural = 'Multiple choice answers'
        ordering = ['custom_order']


class MCQuestionAttempt(QuestionAttempt):
    question = models.ForeignKey(MCQuestion, on_delete=models.PROTECT)
    correct = models.NullBooleanField(blank=True, null=True)
    answer = models.ForeignKey(MCAnswer, on_delete=models.PROTECT)
    answer_content = models.CharField('student answer', max_length=1000)

    def __str__(self):
        return "%s - %s - Course %s (attempt %s): answer id %s" % \
            (self.student.get_full_name(),
             self.quiz.name,
             self.course.name,
             self.attempt_number,
             self.answer_id)

    class Meta:
        verbose_name = "Multiple choice questions attempt"
        verbose_name_plural = "Multiple choice questions attempts"


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


class QuestionGroupHeader(Question):

    def __str__(self):
        return self.content
