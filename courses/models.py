from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils.managers import InheritanceManager
from model_utils.models import TimeStampedModel


class Course(models.Model):
    name = models.CharField(
        _("name"),
        max_length=100,
        unique=True,
        help_text=_("Course name (max 100 characters)"),
    )
    code = models.CharField(
        _("course code"), max_length=10, help_text=_("Course code (max 10 characters)")
    )
    description = models.TextField(
        _("description"),
        max_length=800,
        help_text=_("Course description (max 800 characters)"),
    )
    author = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="course", verbose_name=_("author")
    )
    start_date = models.DateTimeField(_("start date"), blank=True, null=True)
    end_date = models.DateTimeField(_("end date"), blank=True, null=True)
    students = models.ManyToManyField(
        User, related_name="member", verbose_name=_("students")
    )
    instructors = models.ManyToManyField(
        User, related_name="instructor", verbose_name=_("instructors")
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
        output = "ID {0} - {1}".format(self.pk, self.name)
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
    ]

    related_name = "sections"
    name = models.CharField(
        _("name"),
        max_length=15,
        unique=False,
        help_text=_("Section name (max 15 characters)"),
    )
    description = models.TextField(
        _("description"),
        max_length=800,
        blank=True,
        null=True,
        help_text=_("Course description (max 800 characters)"),
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
    requirement = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name=related_name,
        verbose_name=_("requirement"),
    )
    published = models.BooleanField(_("published"), default=False)
    create_discussions = models.BooleanField(
        _("create discussion"),
        default=False,
        help_text=_(
            "* FOR UPLOAD SECTION ONLY *: automatically create a discussion board based on participant's video submissions."
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
        default=True,
        help_text=_("* FOR VIDEO SECTION ONLY *: enables displaying video thumbnails."),
    )
    custom_order = models.PositiveIntegerField(
        _("custom order"), default=0, blank=False, null=False
    )

    def clean(self):
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

    def __str__(self):
        return self.name

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
