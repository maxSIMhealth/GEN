from core.support_methods import user_directory_path
from courses.models import SectionItem
from tinymce.models import HTMLField
from upload_validator import FileTypeValidator

from django.db import models
from django.utils.translation import gettext_lazy as _
from GEN.support_methods import duplicate_object


class ContentItem(SectionItem):
    content = HTMLField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.pdffile is None:
            self.item_type = SectionItem.SECTION_ITEM_CONTENT
        super().save(*args, **kwargs)

    def duplicate(self, **kwargs):
        return duplicate_object(self, **kwargs)


class ImageFile(SectionItem):
    file = models.ImageField(
        _("image"), upload_to=user_directory_path, help_text=_("Image file.")
    )

    def __str__(self):
        return "%s - %s" % (self.name, self.description)

    def save(self, *args, **kwargs):
        self.item_type = SectionItem.SECTION_ITEM_IMAGE
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.file.delete()  # Delete the actual image file
        super().delete(*args, **kwargs)  # Call the "real" delete() method.

    def duplicate(self, **kwargs):
        return duplicate_object(self, **kwargs)


class PdfFile(ContentItem):
    file = models.FileField(
        _("pdf"),
        upload_to=user_directory_path,
        help_text=_("Format accepted: PDF."),
        validators=[FileTypeValidator(allowed_types=["application/pdf"])],
    )

    def __str__(self):
        return "%s" % self.name

    def save(self, *args, **kwargs):
        self.item_type = SectionItem.SECTION_ITEM_PDF
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.file.delete()  # Delete the actual pdf file
        super().delete(*args, **kwargs)  # Call the "real" delete() method.

    def duplicate(self, published=None, file=None, suffix=None, section=None, **kwargs):
        # return duplicate_object(self, **kwargs)
        if suffix:
            self.name += f" {suffix}"

        new_pdf = PdfFile(
            name=self.name,
            author=self.author,
            content=self.content,
        )

        if published:
            new_pdf.published = published
        else:
            new_pdf.published = self.published

        if section:
            new_pdf.section = section
        else:
            new_pdf.section = self.section

        if file:
            new_pdf.file.save(self.file.name, self.file)

        new_pdf.save()

        return new_pdf
