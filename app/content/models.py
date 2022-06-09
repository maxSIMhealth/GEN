import logging

from core.support_methods import user_directory_path, user_directory_path_not_random
from courses.models import SectionItem
from upload_validator import FileTypeValidator

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from GEN.storage_backends import MediaStorage
from GEN.support_methods import duplicate_object

# Get an instance of a logger
logger = logging.getLogger(__name__)


class ContentItem(SectionItem):
    def save(self, *args, **kwargs):
        if hasattr(self, "pdffile") is False:
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


class ExternalObject(SectionItem):
    """
    External objects/packages that will be displayed embedded into a section. E.g.:
    iSpring HTML output as a .zip file.

    Note: the package must be a .zip file, and it must have an index.html file at its root.
    """

    file = models.FileField(
        _("Zip package"),
        upload_to=user_directory_path_not_random,
        help_text=_(
            "Format accepted: zip. An 'index.html' file needs to exist in the root of the zip file."
        ),
        # storage=PrivateMediaStorage(),
        validators=[FileTypeValidator(allowed_types=["application/zip"])],
    )
    directory = models.CharField(
        _("directory"),
        max_length=255,
        null=True,
        blank=True,
    )
    url = models.URLField(blank=True)

    def __str__(self):
        return f"{self.name}"

    def save(self, *args, **kwargs):
        self.item_type = SectionItem.SECTION_ITEM_ZIP
        # if bool(self.file):
        #     self.name = self.file.name.split(".")[0].replace(" ", "_")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        import datetime

        media_storage = MediaStorage()

        # copy the zip file into an archival directory
        # date stored in GMT
        current_date = datetime.datetime.now().strftime("%Y-%m-%d/%Hh%Mm%Ss")
        current_path = self.file.name
        username = self.file.name.split("/")[0]
        filename = self.file.name.split("/")[1]
        archival_path = f"archival/{username}/{current_date}-{filename}"

        # check if the file exists in the S3 storage, and then copy it into archival
        if media_storage.exists(current_path):
            copy_successful = media_storage.copy(
                from_path=current_path, to_path=archival_path
            )
            if not copy_successful:
                logger.error(f"Failed to copy file: {self.file.name}")
                raise ValueError("Failed to copy file.")
            else:
                logger.info(f"Successfully copied file: {self.file.name}")

        # check if extracted directory exists in the S3 storage, and then delete it
        if media_storage.directory_exists(self.directory):
            delete_successful = media_storage.delete_directory(self.directory)
            if not delete_successful:
                logger.error(f"Failed to delete directory: {self.directory}")
                raise ValueError("Failed to delete directory.")
            else:
                logger.info(f"Successfully deleted directory: {self.file.name}")

        # delete original zip file
        self.file.delete()

        super().delete(*args, **kwargs)  # Call the "real" delete() method.

    def clean(self):
        # check if zip file contains index.html on root level
        import zipfile

        with zipfile.ZipFile(self.file.file) as zip_file:
            namelist = zip_file.namelist()
            if not namelist.__contains__("index.html"):
                raise ValidationError(
                    _(
                        "Zip file MUST contain an 'index.html' "
                        "file at its base/root level."
                    )
                )

    def unzip_package(self, request):
        import os
        import zipfile
        from pathlib import Path

        from django.contrib import messages

        media_storage = MediaStorage()
        zip_path = Path(self.file.name).with_suffix("")
        zip_url = os.path.splitext(self.file.url)[0]  # stripped .zip extension from url
        output_path = f"{zip_path}_dir"
        url = f"{zip_url}_dir/index.html"

        # extract files
        try:
            with zipfile.ZipFile(self.file.file) as zip_file:
                # check if directory already exists
                directory_exists = media_storage.directory_exists(output_path)

                # extract file if directory does not exist
                if not directory_exists:
                    for filename in zip_file.namelist():
                        file_info = zip_file.getinfo(filename)
                        if not file_info.is_dir():
                            media_storage.save(
                                f"{output_path}/{filename}", zip_file.open(filename)
                            )
                else:
                    messages.error(
                        request,
                        _("Cannot extract zip file. Directory already exists."),
                        extra_tags="error",
                    )
                    return

                messages.success(request, _("Successfully extracted file(s)."))

        except (zipfile.BadZipfile, RuntimeError):
            logger.error(f"Failed extracting zip file: {self.file.name}")
            raise ValueError("Failed extracting zip file.")

        # update directory and url fields
        self.directory = output_path
        self.url = url
        self.save(update_fields=["directory", "url"])
