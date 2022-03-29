from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel

from core.support_methods import user_directory_path
from courses.models import SectionItem
from tinymce.models import HTMLField
from upload_validator import FileTypeValidator


class ContentItem(SectionItem):
    content = HTMLField(
        blank=True,
        null=True
    )


class ImageFile(SectionItem):
    file = models.ImageField(
        _("image"),
        upload_to=user_directory_path,
        help_text=_("Image file.")
    )

    def __str__(self):
        return "%s - %s" % (self.name, self.description)


class PdfFile(ContentItem):
    file = models.FileField(
        _("pdf"),
        upload_to=user_directory_path,
        help_text=_("Format accepted: PDF."),
        validators=[FileTypeValidator(allowed_types=["application/pdf"])],
    )

    def __str__(self):
        return "%s" % (self.name)
