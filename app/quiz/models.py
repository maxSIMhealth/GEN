from django.contrib.auth.models import User
from django.contrib.postgres.fields import IntegerRangeField
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from GEN.support_methods import duplicate_item, duplicate_name
from model_utils.models import TimeStampedModel

from courses.models import Course, Section, SectionItem
from videos.models import VideoFile

QUESTION_TYPES = [
    ("H", _("Header")),
    ("L", _("Likert")),
    ("O", _("Open ended")),
    ("M", _("Multiple choice")),
]

NONE = "NO"
MIN_PERCENTAGE = "MP"
MAX_NUM_MISTAKES = "MN"

ASSESSMENT_METHODS = [
    (NONE, _("None")),
    (MIN_PERCENTAGE, _("Minimum Percentage")),
    (MAX_NUM_MISTAKES, _("Maximum Number of Mistakes")),
]


class Quiz(SectionItem):
    """
    Quiz model
    """

    check_score = models.BooleanField(_("check score"), default=True)
    show_score = models.BooleanField(_("show score"), default=False)
    show_correct_answers = models.BooleanField(_("show correct answers"), default=False)
    assessment_method = models.CharField(
        _("assessment method"),
        max_length=2,
        default=NONE,
        choices=ASSESSMENT_METHODS,
        help_text=_("method for assessing if the quiz has been"),
    )
    assessment_min_percentage = models.PositiveIntegerField(
        _("minimum percentage acceptable"),
        default=80,
        help_text=_(
            "If the participant score percentage is below this value, the quiz is marked as failed"
        ),
    )
    assessment_max_mistakes = models.PositiveIntegerField(
        _("maximum number of mistakes"),
        default=0,
        help_text=_(
            "If the participant exceeds this value, the quiz is marked as failed"
        ),
    )
    require_answers = models.BooleanField(
        _("require participant to answer all questions"), default=False
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.PROTECT,
        related_name="quizzes",
        verbose_name=_("course"),
    )
    video = models.ForeignKey(
        VideoFile,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="quizzes",
        verbose_name=_("video"),
    )
    requirement = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name=_("requirement"),
    )
    allow_multiple_attempts = models.BooleanField(
        _("Allow multiple attempts"), default=False
    )
    attempts_max_number = models.PositiveIntegerField(
        _("attempts max number"), default=1
    )

    class Meta:
        verbose_name = _("quiz")
        verbose_name_plural = _("quizzes")

    def get_questions(self):
        return self.questions.all().select_subclasses()

    def duplicate(self):
        return duplicate_item(self, callback=duplicate_name)


class Question(TimeStampedModel):
    """
    Parent class for questions (Multiple Choice, Likert Scale and Open Ended)
    and for question headers.
    """

    question_type = models.CharField(
        _("question type"), max_length=1, choices=QUESTION_TYPES
    )
    quiz = models.ForeignKey(
        Quiz,
        verbose_name=_("quiz"),
        related_name="questions",
        blank=False,
        on_delete=models.CASCADE,
    )
    content = models.CharField(
        _("content"),
        max_length=1000,
        blank=False,
        help_text=_("Enter the content that you want displayed."),
    )
    explanation = models.TextField(
        _("explanation"),
        blank=True,
        help_text=_("Explanation to be shown after the question has been answered."),
    )
    value = models.PositiveIntegerField(
        _("value"),
        default=1,
        help_text=_("Value to add to the quiz score if the participant answer the question correctly.")
    )
    multiple_correct_answers = models.BooleanField(
        _("multiple correct answers"),
        blank=False,
        default=False,
        help_text=_(
            "Does this question have multiple correct answers (allow user to select multiple answer items)?"
        ),
    )
    custom_order = models.PositiveIntegerField(
        _("custom order"), default=0, blank=False, null=False
    )

    class Meta:
        verbose_name = _("question")
        verbose_name_plural = _("questions")
        ordering = ["custom_order"]

    def __str__(self):
        return self.content


class QuestionGroupHeaderManager(models.Manager):
    def get_queryset(self):
        queryset = (
            super(QuestionGroupHeaderManager, self)
            .get_queryset()
            .filter(question_type="H")
        )
        return queryset


class LikertManager(models.Manager):
    def get_queryset(self):
        queryset = super(LikertManager, self).get_queryset().filter(question_type="L")
        return queryset

    def create(self, **kwargs):
        kwargs.update({"question_type": "L"})
        return super(LikertManager, self).create(**kwargs)


class OpenEndedManager(models.Manager):
    def get_queryset(self):
        queryset = (
            super(OpenEndedManager, self).get_queryset().filter(question_type="O")
        )
        return queryset


class MCQuestionManager(models.Manager):
    def get_queryset(self):
        queryset = (
            super(MCQuestionManager, self).get_queryset().filter(question_type="M")
        )
        return queryset


class Likert(Question):
    """Likert Model"""

    objects = LikertManager()

    class Meta:
        proxy = True
        verbose_name = _("likert question")
        verbose_name_plural = _("likert questions")

    def get_answers(self):
        return LikertAnswer.objects.filter(question=self)

    def check_if_correct(self, likert, guess):
        is_correct = False
        if likert.answer_range.upper:
            # incrementing max value by 1 because the upper bound is always excluded from the range
            correct_range = range(
                likert.answer_range.lower, likert.answer_range.upper + 1
            )
            is_correct = bool(guess in correct_range)
        else:
            correct_value = likert.answer_range.lower
            is_correct = guess == correct_value
        return is_correct

    def __str__(self):
        return "%s" % self.content

    # def get_changeform_initial_data(self, request):
    #     return {"question_type": "L"}


class LikertAnswer(TimeStampedModel):
    """
    Likert answer (scale) model.
    Minimum and maximum values are used to generate the scale layout.
    """

    question = models.OneToOneField(
        Likert, on_delete=models.CASCADE, verbose_name=_("question")
    )
    scale_range = IntegerRangeField(
        _("scale range values"),
        blank=False,
        default=([1, 5]),
        help_text=_("Set the likert scale values."),
    )
    check_answer = models.BooleanField(
        _("check answer"),
        blank=False,
        default=False,
        help_text=_("Check the answer value?"),
    )
    answer_range = IntegerRangeField(
        _("answer range values"),
        blank=True,
        default=([2, 3]),
        help_text=_("Set the minimum and maximum acceptable values."),
    )
    legend = models.TextField(
        _("legend"), blank=True, help_text=_("Legend for the likert scale values.")
    )
    # answer_range = IntegerRangeField()

    def __str__(self):
        return "%s : scale %s to %s" % (
            self.question.content,
            self.scale_range.lower,
            self.scale_range.upper,
        )

    def clean(self):
        # Don't allow answer scale to be out of the scale range bounds
        if self.answer_range.lower:
            if self.answer_range.lower < self.scale_range.lower:
                raise ValidationError(
                    _("The answer range must not exceed the scale range.")
                )
        elif self.answer_range.upper:
            if self.answer_range.upper > self.scale_range.upper:
                raise ValidationError(
                    _("The answer range must not exceed the scale range.")
                )
        return super().clean()

    class Meta:
        verbose_name = _("likert answer (scale definition)")
        verbose_name_plural = _("likert answers (scale definition)")


class OpenEnded(Question):
    """
    Open Ended model
    """

    objects = OpenEndedManager()

    # def __str__(self):
    #     return ("%s") % (self.content)

    class Meta:
        proxy = True
        verbose_name = _("open ended question")
        verbose_name_plural = _("open ended questions")


class MCQuestion(Question):

    objects = MCQuestionManager()

    class Meta:
        proxy = True
        verbose_name = _("multiple choice question")
        verbose_name_plural = _("multiple choice questions")

    def check_if_correct(self, guess):
        answer = MCAnswer.objects.get(id=guess)

        return bool(answer.check)

    def get_answers(self):
        return MCAnswer.objects.filter(question=self)

    def get_answers_list(self):
        return [
            (answer.id, answer.content)
            for answer in MCAnswer.objects.filter(question=self)
        ]


class MCAnswer(TimeStampedModel):
    """
    Multiple choice question answer
    """

    question = models.ForeignKey(
        MCQuestion,
        on_delete=models.CASCADE,
        related_name="answers",
        verbose_name=_("question"),
    )

    content = models.CharField(
        _("content"),
        max_length=1000,
        blank=False,
        help_text=_("Enter the answer text that you want displayed"),
    )

    check = models.BooleanField(
        _("check"),
        blank=False,
        default=False,
        help_text=_("Should this answer be checked/marked?"),
    )

    custom_order = models.PositiveIntegerField(
        _("custom order"), default=0, blank=False, null=False
    )

    def __str__(self):
        return self.content

    class Meta:
        verbose_name = _("multiple choice answer")
        verbose_name_plural = _("multiple choice answers")
        ordering = ["custom_order"]


class QuestionAttempt(TimeStampedModel):
    question_type = models.CharField(
        _("question type"), max_length=1, choices=QUESTION_TYPES
    )
    student = models.ForeignKey(
        User, on_delete=models.PROTECT, verbose_name=_("student")
    )
    quiz = models.ForeignKey(Quiz, on_delete=models.PROTECT, verbose_name=_("quiz"))
    course = models.ForeignKey(
        Course, on_delete=models.PROTECT, verbose_name=_("course")
    )
    section = models.ForeignKey(
        Section, on_delete=models.PROTECT, verbose_name=_("section")
    )
    attempt_number = models.PositiveIntegerField(_("attempt number"), default=0)
    question = models.ForeignKey(
        Question, on_delete=models.PROTECT, verbose_name=_("question")
    )
    multiplechoice_answer = models.ForeignKey(
        MCAnswer,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        verbose_name=_("multiple choice answer item"),
    )
    video = models.ForeignKey(
        VideoFile,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        verbose_name=_("video"),
    )
    answer_content = models.TextField(_("student answer"), null=True, blank=True)
    correct = models.BooleanField(_("correct"), blank=True, null=True)
    # likert_answer_content = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        verbose_name = _("question attempt")
        verbose_name_plural = _("question attempts")

    def __str__(self):
        return "%s - %s - Course %s (attempt %s): %s" % (
            self.student.get_full_name(),
            self.quiz.name,
            self.course.name,
            self.attempt_number,
            self.question,
        )


class LikertAttemptManager(models.Manager):
    def get_queryset(self):
        queryset = (
            super(LikertAttemptManager, self).get_queryset().filter(question_type="L")
        )
        return queryset

    def create(self, **kwargs):
        kwargs.update({"question_type": "L"})
        return super(LikertAttemptManager, self).create(**kwargs)


class OpenEndedAttemptManager(models.Manager):
    def get_queryset(self):
        queryset = (
            super(OpenEndedAttemptManager, self)
            .get_queryset()
            .filter(question_type="O")
        )
        return queryset

    def create(self, **kwargs):
        kwargs.update({"question_type": "O"})
        return super(OpenEndedAttemptManager, self).create(**kwargs)


class MCQuestionAttemptManager(models.Manager):
    def get_queryset(self):
        queryset = (
            super(MCQuestionAttemptManager, self)
            .get_queryset()
            .filter(question_type="M")
        )
        return queryset

    def create(self, **kwargs):
        kwargs.update({"question_type": "M"})
        return super(MCQuestionAttemptManager, self).create(**kwargs)


class LikertAttempt(QuestionAttempt):
    """
    Likert Attempt model
    """

    objects = LikertAttemptManager()

    class Meta:
        proxy = True
        verbose_name = _("likert attempt")
        verbose_name_plural = _("likert attempts")


class OpenEndedAttempt(QuestionAttempt):
    """
    Open Ended Attempt model
    """

    objects = OpenEndedAttemptManager()

    class Meta:
        proxy = True
        verbose_name = _("open ended attempt")
        verbose_name_plural = _("open ended attempts")


class MCQuestionAttempt(QuestionAttempt):
    """
    Multiple Choice Attempt model
    """

    objects = MCQuestionAttemptManager()

    class Meta:
        proxy = True
        verbose_name = _("multiple choice questions attempt")
        verbose_name_plural = _("multiple choice questions attempts")


class QuizScore(TimeStampedModel):
    student = models.ForeignKey(
        User, on_delete=models.PROTECT, verbose_name=_("student")
    )
    quiz = models.ForeignKey(Quiz, on_delete=models.PROTECT, verbose_name=_("quiz"))
    course = models.ForeignKey(
        Course, on_delete=models.PROTECT, verbose_name=_("course")
    )
    score = models.PositiveIntegerField(_("score"), default=0)
    max_score = models.PositiveIntegerField(_("max score"), default=0)
    completed = models.BooleanField(
        _("completed successfully"),
        default=False,
        help_text=_(
            "If quiz assessment is enabled, this field represents if the participant achieved a passing score or not."
        ),
    )

    class Meta:
        verbose_name = _("quiz score")
        verbose_name_plural = _("quiz scores")

    def __str__(self):
        return "Score for user %s - quiz %s - course %s" % (
            self.student.username,
            self.quiz.name,
            self.course.name,
        )


class QuestionGroupHeader(Question):
    objects = QuestionGroupHeaderManager()

    class Meta:
        proxy = True
        verbose_name = _("question group header")
        verbose_name_plural = _("question group headers")

    def __str__(self):
        return self.content
