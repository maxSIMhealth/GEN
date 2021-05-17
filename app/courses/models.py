from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils.managers import InheritanceManager
from model_utils.models import TimeStampedModel
from tinymce.models import HTMLField


class Course(models.Model):
    name = models.CharField(
        _("name"),
        max_length=100,
        unique=False,
        help_text=_("Course name (max 100 characters)"),
    )
    code = models.CharField(
        _("course code"),
        unique=True,
        max_length=10,
        help_text=_("Unique course code (max 10 characters)"),
    )
    description = models.TextField(
        _("description"),
        max_length=1500,
        help_text=_("Description (max 1500 characters)"),
    )
    author = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="course", verbose_name=_("author")
    )
    start_date = models.DateTimeField(_("start date"), blank=True, null=True)
    end_date = models.DateTimeField(_("end date"), blank=True, null=True)
    members = models.ManyToManyField(
        User,
        related_name="member",
        verbose_name=_("members"),
        help_text=_("List of all users that should have access to the course (including instructors).")
    )
    learners = models.ManyToManyField(
        User,
        related_name="learners",
        verbose_name=_("learners"),
        help_text=_("List of learners (students)."),
        blank=True,
    )
    learners_max_number = models.IntegerField(
        _("learners max number"),
        blank=True,
        null=True,
        help_text=_("maximum number of learners"),
    )
    instructors = models.ManyToManyField(
        User,
        related_name="instructor",
        verbose_name=_("instructors"),
        help_text=_("List of instructors. These users will be able to edit the course's content and structure.")
    )
    blind_data = models.BooleanField(
        _("blind data"),
        default=False,
        help_text=_("Defines if user data (e.g., name) should be visible or not."),
    )
    enable_gamification = models.BooleanField(
        _("gamification"),
        default=True,
        help_text=_("Enables voting in discussions and comments"),
    )
    show_scoreboard = models.BooleanField(
        _("show scoreboard"), default=True, help_text=_("Requires gamification")
    )
    show_leaderboard = models.BooleanField(
        _("show leaderboard"), default=True, help_text=_("Requires gamification")
    )
    show_progress_tracker = models.BooleanField(
        _("show progress tracker"), default=True
    )

    class Meta:
        verbose_name = _("course")
        verbose_name_plural = _("courses")

    def __str__(self):
        output = "ID {0} - {1} - {2}".format(self.pk, self.code, self.name)
        return output

    def clean(self):
        # check course dates
        if self.start_date and self.end_date:
            if self.end_date <= self.start_date:
                raise ValidationError(
                    _(
                        "Course end date cannot be equal or \
                        earlier than the start date."
                    )
                )
        # check gamification components
        if self.show_scoreboard and not self.enable_gamification:
            raise ValidationError(_("Scoreboard requires gamification to be enabled"))
        if self.show_leaderboard and not self.enable_gamification:
            raise ValidationError(_("Leaderboard requires gamification to be enabled"))


class Section(models.Model):
    SECTION_TYPES = [
        ("D", _("Discussion boards")),
        ("V", _("Videos")),
        ("Q", _("Quizzes")),
        ("U", _("Uploads")),
        ("C", _("Content")),
    ]

    related_name = "sections"
    name = models.CharField(
        _("name"),
        max_length=20,
        unique=False,
        help_text=_("Section name (max 20 characters)"),
    )
    description = models.TextField(
        _("description"),
        max_length=1000,
        blank=True,
        null=True,
        help_text=_("Description (max 1000 characters)"),
    )
    content = HTMLField(
        blank=True,
        null=True
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name=related_name,
        verbose_name=_("course"),
    )
    section_type = models.CharField(
        _("section type"), max_length=1, choices=SECTION_TYPES
    )
    start_date = models.DateTimeField(_("start date"), blank=True, null=True)
    end_date = models.DateTimeField(_("end date"), blank=True, null=True)
    requirement = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name=related_name,
        verbose_name=_("requirement"),
    )
    published = models.BooleanField(_("published"), default=False)
    pre_assessment = models.BooleanField(
        _("pre-assessment"),
        default=False,
        help_text=_(
            "* FOR QUIZ SECTION ONLY *: Is this section a pre-assessment to evaluate if the learner needs to go "
            "through the course/module?")
    )
    create_discussions = models.BooleanField(
        _("create discussion"),
        default=False,
        help_text=_(
            "* FOR UPLOAD SECTION ONLY *: automatically create a discussion board based on participant's video "
            "submissions. "
        ),
    )
    section_output = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="sections_output",
        help_text=_(
            "* FOR UPLOAD SECTION ONLY *: Define the section in which to create the discussion boards."
        ),
        verbose_name=_("section output"),
    )
    show_thumbnails = models.BooleanField(
        _("show thumbnails"),
        default=False,
        help_text=_(
            "* FOR VIDEO AND UPLOAD SECTIONS ONLY *: enables displaying video thumbnails."
        ),
    )
    custom_order = models.PositiveIntegerField(
        _("custom order"), default=0, blank=False, null=False
    )

    def clean(self):
        # check course dates
        if self.start_date and self.end_date:
            if self.end_date <= self.start_date:
                raise ValidationError(
                    _(
                        "Course end date cannot be equal or \
                        earlier than the start date."
                    )
                )
        # check parameters related to Upload Section
        if (
            self.create_discussions or self.section_output
        ) and not self.section_type == "U":
            raise ValidationError(
                _(
                    "To set 'create discussion' or 'section output', the section type must be Upload."
                )
            )
        if self.create_discussions and not self.section_output:
            raise ValidationError(
                _("To create a discussion you must select a discussion section output.")
            )
        if self.section_output and not self.create_discussions:
            raise ValidationError(
                _(
                    "You can not select a section output if 'create discussions' is not enabled."
                )
            )
        # check parameters related to Video and Upload Sections
        if self.show_thumbnails and not (self.section_type == 'V' or self.section_type == 'U'):
            raise ValidationError(
                _("To enable 'show thumbnails', the section type must be Video or Upload")
            )
        # check parameters related to Quiz Section
        if self.pre_assessment and not self.section_type == "Q":
            raise ValidationError(
                _("To enable 'pre assessment', the section type must be Quiz.")
            )

    def __str__(self):
        output = "ID {0} - {1}".format(self.pk, self.name)
        return output

    class Meta:
        verbose_name = _("section")
        verbose_name_plural = _("sections")
        ordering = ["custom_order"]


class SectionItem(TimeStampedModel):
    name = models.CharField(_("name"), max_length=80, unique=False)
    related_name = "section_items"
    description = models.TextField(
        _("description"),
        max_length=400,
        help_text=_("Brief description (max 400 characters)"),
        blank=True,
        null=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name=related_name,
        verbose_name=_("author"),
    )
    start_date = models.DateTimeField(_("start date"), blank=True, null=True)
    end_date = models.DateTimeField(_("end date"), blank=True, null=True)
    section = models.ForeignKey(
        Section,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name=related_name,
        verbose_name=_("section"),
    )
    published = models.BooleanField(_("published"), default=False)
    show_related_content = models.BooleanField(
        _("show related content"),
        default=False,
        help_text=_("Display content related to this item (e.g., quizzes related to a video)")
    )
    custom_order = models.PositiveIntegerField(
        _("custom order"), default=0, blank=False, null=False
    )

    objects = InheritanceManager()

    class Meta:
        verbose_name = _("section item")
        verbose_name_plural = _("section items")
        ordering = ["custom_order"]

    def __str__(self):
        output = "ID {0} - {1}".format(self.pk, self.name)
        return output


class Status(TimeStampedModel):
    learner = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name=_("learner")
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.PROTECT,
        verbose_name=_("course")
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.PROTECT,
        related_name="status",
        verbose_name=_("section")
    )
    completed = models.BooleanField(
        _("section completed successfully"),
        default=False,
        help_text=_("Whether the section has been marked as complete or not.")
    )

    class Meta:
        verbose_name = _("section status")
        verbose_name_plural = _("sections status")
        unique_together = ["learner", "course", "section"]
