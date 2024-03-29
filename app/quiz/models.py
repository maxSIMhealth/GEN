import math

from content.models import ImageFile
from courses.models import Course, Section, SectionItem
from model_utils.models import TimeStampedModel
from quiz.support_methods import duplicate_question, duplicate_quiz
from tinymce.models import HTMLField
from videos.models import VideoFile

from django.contrib.auth.models import User
from django.contrib.postgres.fields import IntegerRangeField
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

QUESTION_TYPES = [
    ("H", _("Header")),
    ("L", _("Likert")),
    ("O", _("Open ended")),
    ("M", _("Multiple choice")),
]

MIN_PERCENTAGE = "MP"
MAX_NUM_MISTAKES = "MN"

ASSESSMENT_METHODS = [
    (MIN_PERCENTAGE, _("Minimum Percentage")),
    (MAX_NUM_MISTAKES, _("Maximum Number of Mistakes")),
]


class Quiz(SectionItem):
    """
    Quiz model
    """

    paginate = models.BooleanField(_("paginate questions"), default=True)
    graded = models.BooleanField(
        _("graded quiz"),
        default=True,
        help_text=_("Defines if the quiz will be graded."),
    )
    show_score = models.BooleanField(
        _("show score"),
        default=False,
        help_text=_(
            "Defines if the quiz score and assessment will be shown in the results page."
        ),
    )
    show_question_value = models.BooleanField(_("show question value"), default=True)
    show_correct_answers = models.BooleanField(_("show correct answers"), default=False)
    show_submissions_count = models.BooleanField(
        _("show submissions count"),
        default=False,
        help_text=_(
            "Defines if the total number of submissions should be visible to ALL users "
            "(including learners). If false, only the quiz author, instructors, and "
            "admins will be able to see this information."
        ),
    )
    limit_submissions = models.BooleanField(
        default=False,
        help_text=_(
            "Defines if the quiz should be disabled after reaching a specific number "
            "of submissions."
        ),
    )
    limit_submissions_max = models.PositiveIntegerField(
        _("Limit number of submissions"),
        default=1,
        help_text=_("Maximum number of submissions allowed for the quiz.")
    )
    max_score = models.PositiveIntegerField(
        _("max score"),
        default=0,
        help_text=_(
            "** NOT IN USE ** Maximum score automatically based on questions values."
        ),
    )
    assessment_method = models.CharField(
        _("assessment method"),
        max_length=2,
        blank=True,
        null=True,
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
        _("require answers"),
        default=False,
        help_text=_("Require participant to answer all questions"),
    )
    randomize = models.BooleanField(
        _("randomize"), default=False, help_text=_("Randomize questions order")
    )
    subset = models.BooleanField(
        _("subset"),
        default=False,
        help_text=_("Enable to use only a subset of the questions of this quiz"),
    )
    subset_number = models.PositiveIntegerField(
        _("subset"), default=0, help_text=_("Number of questions to use on the subset")
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
    show_question_number = models.BooleanField(
        _("Show question number"),
        default=True,
    )
    feedback = HTMLField(
        _("feedback"),
        blank=True,
        help_text=_("Feedback to be shown after the quiz has been answered."),
    )

    class Meta:
        verbose_name = _("quiz")
        verbose_name_plural = _("quizzes")

    def save(self, *args, **kwargs):
        # self.update_max_score()
        self.item_type = SectionItem.SECTION_ITEM_QUIZ
        super(Quiz, self).save(*args, **kwargs)

    def clean(self):
        errors = []

        if self.section and self.section.pre_assessment:
            if self.allow_multiple_attempts:
                errors.append(
                    ValidationError(
                        _(
                            "Enabling multiple attempts is not allowed for quizzes in a 'pre assessment' section."
                        )
                    )
                )

            if self.assessment_method is None:
                errors.append(
                    ValidationError(
                        _(
                            "Having an assessment method defined is required for quizzes in a 'pre assessment' section."
                        )
                    )
                )

        if self.section and self.section.final_assessment:
            if self.assessment_method is None:
                errors.append(
                    ValidationError(
                        _(
                            "Having an assessment method defined is required for quizzes in a 'final assessment' section."
                        )
                    )
                )

        if self.subset:
            if not self.randomize:
                errors.append(
                    ValidationError(
                        _('Enabling subset requires having "randomize" enabled.')
                    )
                )
            if self.subset_number == 0:
                errors.append(
                    ValidationError(
                        _(
                            "Since subset is enabled, subset number must be greater than 0."
                        )
                    )
                )

        if self.limit_submissions:
            if self.limit_submissions_max == 0:
                errors.append(
                    ValidationError(
                        _(
                            "Since limit submissions is enabled, max submissions value must be greater than 0."
                        )
                    )
                )

        if len(errors) > 0:
            raise ValidationError(errors)
        else:
            return super().clean()

    # def update_max_score(self):
    #     if self.questions.exists():
    #         # update max score based on questions
    #         max_score = \
    #             self.questions.all().exclude(question_type='H').exclude(question_type='O').aggregate(Sum('value'))[
    #                 'value__sum']
    #         self.max_score = max_score
    #     else:
    #         self.max_score = 0

    def get_questions(self):
        return self.questions.all().select_subclasses()

    # def max_score(self):
    #     return self.questions.all().exclude(question_type='H').exclude(question_type='O').aggregate(Sum('value'))[
    #         'value__sum']

    def duplicate(self, *args, **kwargs):
        return duplicate_quiz(self, *args, **kwargs)


class Question(TimeStampedModel):
    """
    Parent class for questions (Multiple Choice, Likert Scale and Open Ended)
    and for question headers.
    """

    OPENENDED_DATE = "OD"
    OPENENDED_NUMERIC = "ON"
    OPENENDED_TEXTAREA = "OA"
    OPENENDED_TEXT = "OT"
    OPENENDED_EMAIL = "OE"
    OPENENDED_HOUR = "OH"

    OPENENDED_TYPES = [
        (OPENENDED_DATE, _("Open ended - Date")),
        (OPENENDED_NUMERIC, _("Open ended - Numeric")),
        (OPENENDED_HOUR, _("Open ended - Time/hour")),
        (OPENENDED_TEXT, _("Open ended - Text (short)")),
        (OPENENDED_TEXTAREA, _("Open ended - Text (long)")),
        (OPENENDED_EMAIL, _("Open ended - Email")),
    ]

    question_type = models.CharField(
        _("question type"), max_length=1, choices=QUESTION_TYPES
    )
    author = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name=_("author"),
    )
    quiz = models.ForeignKey(
        Quiz,
        verbose_name=_("quiz"),
        related_name="questions",
        blank=False,
        on_delete=models.CASCADE,
    )
    content = HTMLField(
        _("content"),
        max_length=2000,
        blank=False,
        help_text=_("Main text content of the question (max 2000 characters)."),
    )
    additional_content = HTMLField(
        _("additional content"),
        max_length=2000,
        blank=True,
        null=True,
        help_text=_(
            "Optional: additional text that will be shown under the main text content (max 2000 characters)."
        ),
    )
    feedback = HTMLField(
        _("feedback"),
        blank=True,
        help_text=_("Feedback to be shown after the question has been answered."),
    )
    feedback_image = models.ForeignKey(
        ImageFile,
        verbose_name=_("feedback image"),
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        help_text=_(
            "Optional feedback image file to be shown after the question has been answered."
        ),
        related_name="feedback_image",
    )
    feedback_video = models.ForeignKey(
        VideoFile,
        verbose_name=_("feedback_video"),
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        help_text=_(
            "Optional feedback video file to be shown after the question has been answered."
        ),
        related_name="feedback_video",
    )
    image = models.ForeignKey(
        ImageFile,
        verbose_name=_("image"),
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        help_text=_("Optional image file."),
    )
    value = models.PositiveIntegerField(
        _("value"),
        default=1,
        validators=[MinValueValidator(1)],
        help_text=_(
            "Value to add to the quiz score if the participant answer the question correctly."
        ),
    )
    multiple_correct_answers = models.BooleanField(
        _("multiple correct answers"),
        blank=False,
        default=False,
        help_text=_(
            "Does this question have multiple correct answers (allow user to select multiple answer items)?"
        ),
    )
    openended_type = models.CharField(
        _("Open ended type"),
        max_length=2,
        choices=OPENENDED_TYPES,
        default=OPENENDED_TEXTAREA,
        help_text=_("Type of open ended question."),
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

    def duplicate(self, **kwargs):
        return duplicate_question(self, **kwargs)

    def clean(self):
        errors = []

        if self.feedback_image and not self.feedback:
            errors.append(
                ValidationError(
                    _("Feedback text has to defined to enable feedback image.")
                )
            )

        if len(errors) > 0:
            raise ValidationError(errors)
        else:
            return super().clean()


#     def save(self, *args, **kwargs):
#         self.quiz.update_max_score()
#         super(Question, self).save(*args, **kwargs)
#
#
# @receiver(post_save, sender=Question)
# def update_quiz_maxscore(sender, instance, **kwargs):
#     instance.quiz.update_max_score()


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

        return bool(answer.mark)

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
        max_length=2000,
        blank=False,
        help_text=_(
            "Enter the answer text that you want displayed (max 2000 characters)."
        ),
    )

    mark = models.BooleanField(
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


class QuizScore(TimeStampedModel):
    student = models.ForeignKey(
        User, on_delete=models.PROTECT, verbose_name=_("student")
    )
    quiz = models.ForeignKey(Quiz, on_delete=models.PROTECT, verbose_name=_("quiz"))
    course = models.ForeignKey(
        Course, on_delete=models.PROTECT, verbose_name=_("course")
    )
    attempt_number = models.PositiveIntegerField(_("attempt number"), default=0)
    score = models.PositiveIntegerField(_("score"), default=0)
    max_score = models.PositiveIntegerField(_("max score"), default=0)
    num_mistakes = models.PositiveIntegerField(
        _("number of mistakes"),
        default=0,
        help_text=_("Total number of mistakes (incorrect questions)."),
    )
    max_mistakes = models.PositiveIntegerField(
        _("maximum number of mistakes"),
        default=0,
        help_text=_(
            "If the participant exceeds this value, the quiz is marked as failed"
        ),
    )
    min_percentage = models.PositiveIntegerField(
        _("minimum percentage acceptable"),
        default=80,
        help_text=_(
            "If the participant score percentage is below this value, the quiz is marked as failed"
        ),
    )
    completed = models.BooleanField(
        _("completed successfully"),
        default=False,
        help_text=_(
            "If quiz assessment is enabled, this field represents if the participant achieved a passing score or not."
        ),
    )
    expert_feedback = models.BooleanField(
        _("expert feedback"),
        default=False,
        help_text=_("Defines if the quiz was submitted by an expert/instructor."),
    )

    class Meta:
        verbose_name = _("quiz score")
        verbose_name_plural = _("quiz scores")
        unique_together = ["student", "course", "quiz", "attempt_number"]

    def __str__(self):
        return "Score for user %s - quiz %s - course %s" % (
            self.student.username,
            self.quiz.name,
            self.course.name,
        )

    def score_percentage(self):
        percentage = (self.score * 100) / self.max_score
        return math.ceil(percentage)

    # def attempt_increase(self):
    #     self.attempt_number = self.attempt_number + 1
    #     self.save()

    def perform_assessment(self):
        if self.quiz.assessment_method == MIN_PERCENTAGE:
            percentage = self.score_percentage()
            if percentage >= self.min_percentage:
                self.completed = True
            else:
                self.completed = False
        elif self.quiz.assessment_method == MAX_NUM_MISTAKES:
            if self.num_mistakes <= self.max_mistakes:
                self.completed = True
            else:
                self.completed = False
        else:
            self.completed = True

        # self.save()


class QuestionGroupHeader(Question):
    objects = QuestionGroupHeaderManager()

    class Meta:
        proxy = True
        verbose_name = _("question group header")
        verbose_name_plural = _("question group headers")

    def __str__(self):
        return self.content


class QuestionAttempt(TimeStampedModel):
    question_type = models.CharField(
        _("question type"), max_length=1, choices=QUESTION_TYPES
    )
    student = models.ForeignKey(
        User, on_delete=models.PROTECT, verbose_name=_("student")
    )
    quiz = models.ForeignKey(Quiz, on_delete=models.PROTECT, verbose_name=_("quiz"))
    quiz_score = models.ForeignKey(
        QuizScore,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name=_("quiz submission"),
    )
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
        verbose_name=_("multiple choice item"),
    )
    video = models.ForeignKey(
        VideoFile,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        verbose_name=_("video"),
    )
    answer_content = models.TextField(_("Participant answer"), null=True, blank=True)
    correct = models.BooleanField(_("correct"), blank=True, null=True)
    # likert_answer_content = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        verbose_name = _("question attempt")
        verbose_name_plural = _("question attempts")
        ordering = ["created"]

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
