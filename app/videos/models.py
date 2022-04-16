import io
import logging
import os
import tempfile

# from django.core.validators import FileExtensionValidator
from django.core.files.storage import get_storage_class
from django.db import models
from django.utils.translation import gettext_lazy as _
from GEN.support_methods import duplicate_object
from GEN import settings as django_settings
from PIL import Image
from tinymce.models import HTMLField
from upload_validator import FileTypeValidator

from core.support_methods import user_directory_path
from courses.models import Course, SectionItem
from .support_methods import crop_image, read_frame_as_jpeg

# from django.core.files.uploadedfile import InMemoryUploadedFile

# Get an instance of a logger
logger = logging.getLogger(__name__)

# Media storage object to be able to obtain media full url
media_storage = get_storage_class()()


class VideoFileQuerySet(models.QuerySet):
    def delete(self, *args, **kwargs):
        for obj in self:
            obj.file.delete()
            obj.thumbnail.delete()
        super().delete(*args, **kwargs)


class Playlist(SectionItem):
    # FIXME: not being used, consider removing
    course = models.ForeignKey(
        Course,
        on_delete=models.PROTECT,
        related_name="videolists",
        verbose_name=_("course"),
    )

    class Meta:
        verbose_name = _("playlist")
        verbose_name_plural = _("playlists")


class VideoFile(SectionItem):
    objects = VideoFileQuerySet.as_manager()
    related_name = "videos"
    course = models.ForeignKey(
        Course,
        on_delete=models.PROTECT,
        related_name=related_name,
        verbose_name=_("course"),
    )
    uploaded_at = models.DateTimeField(_("uploaded at"), auto_now_add=True)
    content = HTMLField(
        blank=True,
        null=True
    )
    file = models.FileField(
        _("file"),
        upload_to=user_directory_path,
        # validators=[FileExtensionValidator(allowed_extensions=("mp4", "m4v", "mov"))],
        validators=[FileTypeValidator(allowed_types=["video/mp4", "video/quicktime"])],
    )
    subtitle = models.FileField(
        _("subtitle"),
        upload_to=user_directory_path,
        blank=True,
        null=True,
        validators=[FileTypeValidator(allowed_types=["text/plain", ])],
    )
    internal_name = models.CharField(
        _("internal name"),
        max_length=255,
        null=True,
        blank=True,
        help_text=_("Video internal name (not visible to users)."),
    )
    thumbnail = models.ImageField(
        _("thumbnail"), upload_to=user_directory_path, blank=True, null=True
    )
    # discussion = models.ForeignKey(
    #     Discussion, on_delete=models.CASCADE, related_name='video')
    # validators = [FileExtensionValidator(allowed_extensions=("mp4"))]

    class Meta:
        verbose_name = _("video file")
        verbose_name_plural = _("video files")

    def generate_video_thumbnail(self):
        """Generates video thumbnail (square proportion)"""
        video = self
        video_filename = os.path.splitext(video.file.name)[0]
        thumbnail_filename = os.path.split(video_filename)[1] + "_thumb.jpg"
        ffmpeg_tempfile = tempfile.NamedTemporaryFile()
        # video_thumbnail_output = '.' + settings.MEDIA_URL + thumbnail_filename
        size = (128, 128)

        if django_settings.USE_S3:
            # get video full S3 url path
            video_url = media_storage.url(name=video.file.name)
        else:
            # get video full local path
            video_url = video.file.path

        (ffmpeg_output, ffmpeg_error) = read_frame_as_jpeg(
            video_url, "00:00:01.000"
        )

        if ffmpeg_error is None:
            logger.info("Video thumbnail generated ok")
            thumbnail = Image.open(io.BytesIO(ffmpeg_output))
            thumbnail = crop_image(thumbnail)
            thumbnail.thumbnail(size)
            thumbnail.save(ffmpeg_tempfile, "JPEG")
            ffmpeg_tempfile.seek(0)
            logger.info("Video thumbnail resized ok")
        else:
            logger.error("Error generating thumbnail")
            raise ValueError("Error generating thumbnail:" + ffmpeg_error)

        # link thumbnail to video object
        # self.thumbnail = InMemoryUploadedFile(
        # output, 'ImageField', thumbnail_filename, 'image/jpeg', output.tell(), None)

        # define thumbnail file in user directory and link it to video object, postponing save command
        self.thumbnail.save(name=thumbnail_filename, content=ffmpeg_tempfile, save=False)

        # calling save command, specifying that only the thumbnail field will be updated
        # this will be read by the @post_save signal receiver
        self.save(update_fields=['thumbnail'])

        # closes temporary file and allows it to be deleted
        ffmpeg_tempfile.close()

    def delete(self, *args, **kwargs):
        self.file.delete()  # Delete the actual video file
        if self.thumbnail:
            self.thumbnail.delete()  # Delete the thumbnail file
        if self.subtitle:
            self.subtitle.delete()  # Delete the subtitle file
        super().delete(*args, **kwargs)  # Call the "real" delete() method.

    def duplicate(self, **kwargs):
        # return duplicate_item(self, callback=duplicate_name)
        return duplicate_object(self, file=True, **kwargs)

    def save(self, *args, **kwargs):
        self.item_type = SectionItem.SECTION_ITEM_VIDEO
        super().save(*args, **kwargs)


# class MediaFile(models.Model):
#     # FIXME: this should be renamed to DocumentFile or something like that

#     YOUTUBE = "YTB"
#     PDF = "PDF"

#     ATTACHMENT_KINDS = [
#         (PDF, "PDF Document"),
#         (YOUTUBE, "Youtube Video"),
#     ]

#     title = models.CharField(max_length=100, unique=True)
#     kind = models.CharField(max_length=3, choices=ATTACHMENT_KINDS, default=YOUTUBE)
#     author = models.ForeignKey(User, on_delete=models.PROTECT, related_name="medias")
#     url = models.URLField(max_length=200)

#     def __str__(self):
#         return self.title
