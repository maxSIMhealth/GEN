from core.models import CertificateTemplate
from courses.support_methods import duplicate_course
from model_utils.managers import InheritanceManager
from model_utils.models import TimeStampedModel
from tinymce.models import HTMLField

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from GEN.support_methods import duplicate_object

PUBLIC = "P"
LEARNERS = "L"
INSTRUCTORS = "I"
EDITORS = "E"
ADMINS = "A"
PERMISSION_TYPES = [
    (PUBLIC, _("Public")),
    (LEARNERS, _("Learners")),
    (INSTRUCTORS, _("Instructors")),
    (EDITORS, _("Editors")),
    (ADMINS, _("Admins")),
]
COURSE = "C"
MODULE = "M"
COURSE_TYPES = [(COURSE, _("Course")), (MODULE, _("Module"))]
CERTIFICATE_COURSE = "CC"
CERTIFICATE_CUSTOM = "CX"
CERTIFICATE_TYPES = [
    (CERTIFICATE_COURSE, _("Certificate - Course")),
    (CERTIFICATE_CUSTOM, _("Certificate - Custom")),
]


class Course(TimeStampedModel):
    name = models.CharField(
        _("name"),
        max_length=150,
        unique=False,
        help_text=_("Course name (max 150 characters)"),
    )
    code = models.CharField(
        _("course code"),
        unique=True,
        max_length=10,
        help_text=_("Unique course code (max 10 characters)"),
    )
    type = models.CharField(
        _("course type"),
        max_length=1,
        choices=COURSE_TYPES,
        default=COURSE,
        help_text=_(
            "Sets how the course will be called (for aesthetics purpose only, does not affect functionalities)."
        ),
    )
    show_code = models.BooleanField(
        _("show course code"),
        default=False,
        help_text=_("Show course code to instructors."),
    )
    description = HTMLField(
        _("description"),
        help_text=_(
            "Course description. Please try to keep it brief (under 2000 "
            "characters)."
        ),
        blank=True,
        null=True,
    )
    author = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="course", verbose_name=_("author")
    )
    start_date = models.DateTimeField(_("start date"), blank=True, null=True)
    end_date = models.DateTimeField(_("end date"), blank=True, null=True)
    requirement = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name=_("requirement"),
    )
    members = models.ManyToManyField(
        User,
        related_name="member",
        verbose_name=_("members"),
        help_text=_(
            "List of all users that should have access to the course (including instructors)."
        ),
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
        help_text=_(
            "List of instructors. These users will be able to review learners submissions and interact with them."
        ),
    )
    editors = models.ManyToManyField(
        User,
        related_name="editor",
        verbose_name=_("editors"),
        help_text=_(
            "List of editors. These users will be able to edit the course's content and structure."
        ),
    )
    blind_data = models.BooleanField(
        _("blind data"),
        default=False,
        help_text=_("Defines if user data (e.g., name) should be visible or not."),
    )
    provide_certificate = models.BooleanField(
        _("provide certificate"),
        default=False,
        help_text=_("Defines if this course provides a certificate of conclusion."),
    )
    certificate_type = models.CharField(
        _("certificate type"),
        max_length=2,
        choices=CERTIFICATE_TYPES,
        default=CERTIFICATE_COURSE,
        help_text=_(
            "Defines if the certificate provided will be for the current course or use a customized term."
        ),
    )
    certificate_custom_term = models.CharField(
        _("certificate custom term"),
        max_length=150,
        unique=False,
        blank=True,
        help_text=_(
            "Certificate custom term to be used instead of the course/module name."
        ),
    )
    certificate_template = models.ForeignKey(
        CertificateTemplate,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        help_text=_(
            "Certificate template to be used (logos and frame). If no template is defined, certificate will still be created, but on a basic white canvas."
        ),
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
    initial_section_name = models.CharField(
        _("initial section name"),
        max_length=25,
        default="Information",
        unique=False,
        help_text=_(
            "Name for the initial section of the course/module, that shows the description, start/end date, etc."
        ),
    )
    auto_enroll = models.BooleanField(
        _("auto enroll"),
        default=False,
        help_text=_(
            "Defines if new users should automatically be enrolled to this course/module."
        ),
    )

    class Meta:
        verbose_name = _("course")
        verbose_name_plural = _("courses")
        ordering = ["code"]

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
            raise ValidationError(
                {
                    "enable_gamification": _(
                        "Scoreboard requires gamification to be enabled"
                    )
                }
            )
        if self.show_leaderboard and not self.enable_gamification:
            raise ValidationError(
                {
                    "enable_gamification": _(
                        "Leaderboard requires gamification to be enabled"
                    )
                }
            )

        # check certificate components
        if (
            self.certificate_type == CERTIFICATE_CUSTOM
            and not self.certificate_custom_term
        ):
            raise ValidationError(
                {
                    "certificate_custom_term": _(
                        "A custom certificate requires defining a custom term."
                    )
                }
            )

    def type_name(self):
        course_type_val = self.type
        if course_type_val is COURSE:
            course_type = "course"
        elif course_type_val is MODULE:
            course_type = "module"

        return course_type

    def duplicate(self, *args, **kwargs):
        return duplicate_course(self, *args, **kwargs)


class Section(TimeStampedModel):
    SECTION_TYPES = [
        ("D", _("Discussion boards")),
        ("V", _("Videos")),
        ("Q", _("Quizzes")),
        ("U", _("Uploads")),
        ("C", _("Content")),
    ]

    name = models.CharField(
        _("name"),
        max_length=25,
        unique=False,
        help_text=_("Section name (max 25 characters)"),
    )
    description = HTMLField(
        _("description"),
        help_text=_(
            "Section description. Please try to keep it brief (under 1000 "
            "characters or 150 words)."
        ),
        blank=True,
        null=True,
    )
    author = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name=_("author"))
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="sections",
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
        related_name="sections",
        verbose_name=_("requirement"),
    )
    published = models.BooleanField(
        _("published"),
        default=False,
        help_text=_(
            "Published items are visible to all users (based on the 'access restriction' parameter). "
            "Unpublished items are visible only to editors and admins."
        ),
    )
    paginate = models.BooleanField(
        _("paginate items"),
        default=True,
        help_text=_(
            "* FOR CONTENT SECTION ONLY *: Define if section items should be paginated."
        ),
    )
    access_restriction = models.CharField(
        _("access restriction"),
        max_length=1,
        choices=PERMISSION_TYPES,
        default=PUBLIC,
        help_text=_("Define who should have access to this item."),
    )
    author_access_override = models.BooleanField(
        _("access override for author"),
        default=False,
        help_text=_(
            "Define if author should have access to this item, regardless of the access restriction."
        ),
    )
    pre_assessment = models.BooleanField(
        _("pre-assessment"),
        default=False,
        help_text=_(
            "* FOR QUIZ SECTION ONLY *: Is this section a pre-assessment to evaluate if the learner needs to go "
            "through the course/module?"
        ),
    )
    final_assessment = models.BooleanField(
        _("final assessment"),
        default=False,
        help_text=_(
            "* FOR QUIZ SECTION ONLY *: Is this section a final assessment to evaluate if the learner successfully "
            "completed the course/module?"
        ),
    )
    completion_message = models.CharField(
        _("completion message"),
        max_length=200,
        unique=False,
        blank=True,
        help_text=_(
            "A message to be displayed after the participant has successfully completed the section. (max 200 characters)"
        ),
    )
    create_discussions = models.BooleanField(
        _("create discussion"),
        default=False,
        help_text=_(
            "* FOR UPLOAD SECTION ONLY *: automatically create a discussion board based on participant's video "
            "submissions."
        ),
    )
    section_output = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="sections_output",
        help_text=_(
            "* FOR UPLOAD SECTION ONLY *: define the section in which to create the discussion boards."
        ),
        verbose_name=_("section output"),
    )
    output_access_restriction = models.CharField(
        _("output access restriction"),
        max_length=1,
        choices=PERMISSION_TYPES,
        default=PUBLIC,
        help_text=_(
            "* FOR UPLOAD SECTION ONLY *: define who should have access to the new discussion board."
        ),
    )
    output_author_access_override = models.BooleanField(
        _("access override for author"),
        default=False,
        help_text=_(
            "* FOR UPLOAD SECTION ONLY *: define if author should have access, regardless of the access restriction."
        ),
    )
    clone_quiz = models.BooleanField(
        _("clone quiz"),
        default=False,
        help_text=_(
            "* FOR UPLOAD SECTION ONLY *: automatically clones an existing quiz and connect it to the participant's "
            "video after it gets published."
        ),
    )
    clone_quiz_reference = models.ForeignKey(
        "quiz.Quiz",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="clone_quiz_reference",
        help_text=_(
            "* FOR UPLOAD SECTION ONLY *: quiz that will be cloned and connected to the participant's video after"
            "it gets published."
        ),
    )
    clone_quiz_output_section = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="clone_quiz_section",
        help_text=_(
            "* FOR UPLOAD SECTION ONLY *: define the section which the cloned quiz will be related to."
        ),
    )
    clone_quiz_update_owner = models.BooleanField(
        _("update cloned quiz owner"),
        default=False,
        help_text=_("* FOR UPLOAD SECTION ONLY *: updates quiz ownership to uploader"),
    )
    show_thumbnails = models.BooleanField(
        _("show thumbnails"),
        default=False,
        help_text=_(
            "* FOR VIDEO AND UPLOAD SECTIONS ONLY *: enables displaying video thumbnails."
        ),
    )
    show_related_video_name = models.BooleanField(
        _("show related video name"),
        default=False,
        help_text=_("* FOR QUIZ ONLY *: enables displaying related video's name."),
    )
    group_by_video = models.BooleanField(
        _("group by video"),
        default=False,
        help_text=_("* FOR QUIZ ONLY *: group quizzes by videos."),
    )
    custom_order = models.PositiveIntegerField(
        _("custom order"), default=0, blank=False, null=False
    )

    def check_quiz_section_fields(self, errors):
        if not self.section_type == "Q":
            if self.pre_assessment:
                errors.append(
                    ValidationError(
                        _("To enable 'pre assessment', the section type must be Quiz.")
                    )
                )
            if self.final_assessment:
                errors.append(
                    ValidationError(
                        _(
                            "To enable 'final assessment', the section type must be Quiz."
                        )
                    )
                )
        if self.section_type == "Q" and self.pre_assessment and self.final_assessment:
            errors.append(
                ValidationError(
                    _(
                        "A quiz section can not be 'pre assessment' and 'final assessment' simultaneously."
                    )
                )
            )
        if self.show_related_video_name and not self.section_type == "Q":
            errors.append(
                ValidationError(
                    _(
                        "To enable 'show related video name', the section type must be Quiz."
                    )
                )
            )
        if self.group_by_video and not self.section_type == "Q":
            errors.append(
                ValidationError(
                    _("To enable 'group by video', the section type must be Quiz.")
                )
            )

    def check_video_and_upload_fields(self, errors):
        if self.show_thumbnails and not (
            self.section_type == "V" or self.section_type == "U"
        ):
            errors.append(
                ValidationError(
                    _(
                        "To enable 'show thumbnails', the section type must be Video or Upload"
                    )
                )
            )

    def check_upload_section_fields(self, errors):
        if (
            self.create_discussions or self.section_output
        ) and not self.section_type == "U":
            errors.append(
                ValidationError(
                    _(
                        "To set 'create discussion' or 'section output', the section type must be Upload."
                    )
                )
            )
        if (
            self.create_discussions
            and not self.section_output
            and self.section_type == "U"
        ):
            errors.append(
                ValidationError(
                    _(
                        "To create a discussion you must select a discussion section output."
                    )
                )
            )
        if self.section_output and not self.create_discussions:
            errors.append(
                ValidationError(
                    _(
                        "You can not select a section output if 'create discussions' is not enabled."
                    )
                )
            )
        if (
            self.clone_quiz or self.clone_quiz_reference
        ) and not self.section_type == "U":
            errors.append(
                ValidationError(
                    _(
                        "To set 'clone quiz' or 'clone quiz reference', the section type must be Upload."
                    )
                )
            )
        if (
            self.clone_quiz
            and not self.clone_quiz_reference
            and self.section_type == "U"
        ):
            errors.append(
                ValidationError(_("To clone a quiz you must select a quiz reference."))
            )
        if self.clone_quiz_reference and not self.clone_quiz:
            errors.append(
                ValidationError(
                    _(
                        "You can not select a quiz reference if 'clone quiz' is not enabled."
                    )
                )
            )

    def check_section_dates(self, errors):
        if self.start_date and self.end_date:
            if self.end_date <= self.start_date:
                errors.append(
                    ValidationError(
                        _(
                            "Section end date cannot be equal or \
                            earlier than the start date."
                        )
                    )
                )

    def clean(self):
        errors = []

        # check section dates
        self.check_section_dates(errors)
        # check fields related to Upload Section
        self.check_upload_section_fields(errors)
        # check fields related to Video and Upload Sections
        self.check_video_and_upload_fields(errors)
        # check fields related to Quiz Section
        self.check_quiz_section_fields(errors)

        if len(errors) > 0:
            raise ValidationError(errors)
        else:
            return super().clean()

    def __str__(self):
        output = f"ID {self.pk} - {self.name} - part of {self.course}"
        return output

    def duplicate(self, *args, **kwargs):
        return duplicate_object(self, *args, **kwargs)

    class Meta:
        verbose_name = _("section")
        verbose_name_plural = _("sections")
        ordering = ["custom_order"]


class SectionItem(TimeStampedModel):
    SECTION_ITEM_CONTENT = "CON"
    SECTION_ITEM_IMAGE = "IMG"
    SECTION_ITEM_PDF = "PDF"
    SECTION_ITEM_DISCUSSION = "DIS"
    SECTION_ITEM_GAME = "GAM"
    SECTION_ITEM_QUIZ = "QUZ"
    SECTION_ITEM_VIDEO = "VID"

    SECTION_ITEM_TYPES = [
        (SECTION_ITEM_CONTENT, _("Content")),
        (SECTION_ITEM_IMAGE, _("Image")),
        (SECTION_ITEM_DISCUSSION, _("Discussion")),
        (SECTION_ITEM_GAME, _("Game")),
        (SECTION_ITEM_QUIZ, _("Quiz")),
        (SECTION_ITEM_VIDEO, _("Video")),
        (SECTION_ITEM_PDF, _("PDF")),
    ]

    name = models.CharField(_("name"), max_length=120, unique=False)
    description = HTMLField(
        _("description"),
        help_text=_(
            "Item description. Please try to keep it brief (under 1000 "
            "characters or 150 words). Only the first 250 characters will be "
            "shown in the quiz section view."
        ),
        blank=True,
        null=True,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="section_items",
        verbose_name=_("author"),
    )
    start_date = models.DateTimeField(_("start date"), blank=True, null=True)
    end_date = models.DateTimeField(_("end date"), blank=True, null=True)
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="section_items",
        verbose_name=_("section"),
    )
    published = models.BooleanField(_("published"), default=False)
    access_restriction = models.CharField(
        _("access restriction"),
        max_length=1,
        choices=PERMISSION_TYPES,
        default=PUBLIC,
        help_text=_("Define who should have access to this item."),
    )
    author_access_override = models.BooleanField(
        _("access override for author"),
        default=False,
        help_text=_(
            "Define if author should have access to this item, regardless of the access restriction."
        ),
    )
    show_related_content = models.BooleanField(
        _("show related content"),
        default=False,
        help_text=_(
            "Display content related to this item (e.g., quizzes related to a video)"
        ),
    )
    custom_order = models.PositiveIntegerField(
        _("custom order"), default=0, blank=False, null=False
    )
    item_type = models.CharField(
        _("section item type"), max_length=3, choices=SECTION_ITEM_TYPES
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
        User, on_delete=models.PROTECT, related_name="status", verbose_name=_("learner")
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.PROTECT,
        related_name="status",
        verbose_name=_("course"),
    )
    section = models.ForeignKey(
        Section,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="status",
        verbose_name=_("section"),
    )
    completed = models.BooleanField(
        _("item completed successfully"),
        default=False,
        help_text=_("Whether the item has been marked as complete or not."),
    )

    class Meta:
        verbose_name = _("status")
        verbose_name_plural = _("statuses")
        unique_together = ["learner", "course", "section"]

    def __str__(self):
        output = f"ID {self.pk} - Course {self.course} - User {self.learner}"
        if self.section:
            output = output + f" - Section {self.section} - User {self.learner}"

        return output
