from model_utils.models import TimeStampedModel
from sortedm2m.fields import SortedManyToManyField
from tinymce.models import HTMLField

from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _


class LogoFile(TimeStampedModel):
    file = models.ImageField(_("file"), upload_to="uploads/logos/")

    def __str__(self):
        output = "{0}".format(self.file.name.split("/")[-1])
        return output


class CertificateFrameFile(LogoFile):
    class Meta:
        verbose_name = _("certificate frame file")
        verbose_name_plural = _("certificate frame files")


class CertificateLogoFile(LogoFile):
    class Meta:
        verbose_name = _("certificate logo file")
        verbose_name_plural = _("certificate logos files")


class CertificateTemplate(TimeStampedModel):
    name = models.CharField(max_length=50)
    frame = models.ForeignKey(
        CertificateFrameFile,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        help_text=_(
            "Image to be displayed as the certificate frame/border (page size: Letter)."
        ),
    )
    logos = SortedManyToManyField(
        CertificateLogoFile,
        blank=True,
        help_text=_(
            "Logos to be displayed in the header portion of the certificate. Recommended size is 200x80 points."
        ),
    )

    def __str__(self):
        return "%s" % self.name


class FooterLogoFile(LogoFile):
    description = models.CharField(
        _("description"),
        max_length=255,
        help_text=_("Brief description of the logo (max 255 characters)"),
    )
    url = models.URLField(
        max_length=255,
        help_text=_("URL of the destination site when the user clicks on the logo."),
    )
    custom_order = models.PositiveIntegerField(
        _("custom order"), default=0, blank=False, null=False
    )

    class Meta:
        verbose_name = _("footer logo file")
        verbose_name_plural = _("footer logos files")
        ordering = ["custom_order"]


WARNING = "W"
URGENT = "U"
NOTICE = "N"

ALERT_TYPES = [
    (WARNING, _("Warning (yellow)")),
    (URGENT, _("Urgent (red)")),
    (NOTICE, _("Notice (blue)")),
]


class LoginAlertMessage(TimeStampedModel):
    name = models.CharField(max_length=50)
    type = models.CharField(
        max_length=1,
        choices=ALERT_TYPES,
        default=WARNING,
        help_text=_("Defines the visual style of the message."),
    )
    content = HTMLField(
        blank=True,
        null=True,
        max_length=400,
        help_text=_(
            "Message that will be shown at the login page (max 400 characters)."
        ),
    )
    published = models.BooleanField(
        default=False, help_text=_("Sets if the message visible to all users.")
    )
    archived = models.BooleanField(
        default=False,
        help_text=_(
            "Sets if the message is archived and should not be automatically evaluated."
        ),
    )
    show_dates = models.BooleanField(
        default=True,
        help_text=_(
            "Sets if the start and end dates should be visible in the alert message."
        ),
    )
    start_date = models.DateTimeField(
        _("start date"),
        blank=True,
        null=True,
        help_text=_(
            "Date and time of when the message should START being displayed. This will also automatically set 'published' status to True."
        ),
    )
    end_date = models.DateTimeField(
        _("end date"),
        blank=True,
        null=True,
        help_text=_(
            "Date and time of when the message should STOP being displayed.  This will also automatically set the 'published' status to False."
        ),
    )
    custom_order = models.PositiveIntegerField(
        _("custom order"), default=0, blank=False, null=False
    )

    class Meta:
        ordering = ["custom_order"]

    def __str__(self):
        return f"ID {self.pk} - {self.name}"

    def check_if_active(self):
        # checking start date
        if self.start_date:
            if self.start_date <= now():
                self.published = True
            elif self.start_date > now():
                self.published = False

        self.save()

        # checking end date
        if self.end_date:
            if self.end_date > now():
                self.published = True
            elif self.end_date <= now():
                self.published = False
                self.archived = True

        self.save()


class HelpFaq(TimeStampedModel):
    question = models.CharField(
        _("question"),
        max_length=255,
        help_text=_("Question for the Help FAQ (max 255 characters)"),
    )
    answer = HTMLField(
        help_text=_("Answer for the Help FAQ question."),
    )
    custom_order = models.PositiveIntegerField(
        _("custom order"), default=0, blank=False, null=False
    )

    class Meta:
        ordering = ["custom_order"]

    def __str__(self):
        return f"ID {self.pk} - {self.question}"
