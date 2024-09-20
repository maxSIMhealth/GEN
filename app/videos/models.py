import io
import logging
import os
import tempfile

from GEN.settings import AWS_STORAGE_BUCKET_NAME
from core.support_methods import user_directory_path, delete_file_from_s3
from courses.models import Course, SectionItem
from PIL import Image
from upload_validator import FileTypeValidator

# from django.core.validators import FileExtensionValidator
from django.core.files.storage import get_storage_class
from django.db import models
from django.utils.translation import gettext_lazy as _
from GEN import settings as django_settings
from GEN.storage_backends import PrivateMediaStorage
from GEN.support_methods import duplicate_object

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
    file = models.FileField(
        _("file"),
        # upload_to=user_directory_path,
        storage=PrivateMediaStorage(),
        # validators=[FileExtensionValidator(allowed_extensions=("mp4", "m4v", "mov"))],
        validators=[FileTypeValidator(allowed_types=["video/mp4", "video/quicktime"])],
        blank=True,
        null=True,
    )
    original_file_name = models.CharField(max_length=255, blank=True, null=True)
    s3_key = models.CharField(max_length=255, unique=True, blank=True, null=True)
    subtitle = models.FileField(
        _("subtitle"),
        upload_to=user_directory_path,
        storage=PrivateMediaStorage(),
        blank=True,
        null=True,
        validators=[FileTypeValidator(allowed_types=["text/plain", "text/vtt"])],
    )
    internal_name = models.CharField(
        _("internal name"),
        max_length=255,
        null=True,
        blank=True,
        help_text=_("Video internal name (not visible to users)."),
    )
    thumbnail = models.ImageField(
        _("thumbnail"),
        upload_to=user_directory_path,
        storage=PrivateMediaStorage(),
        blank=True,
        null=True,
    )
    mute_audio = models.BooleanField(
        default=False,
        help_text=_("Sets volume to 'mute', but can be manually adjusted by the user.")
    )
    # discussion = models.ForeignKey(
    #     Discussion, on_delete=models.CASCADE, related_name='video')
    # validators = [FileExtensionValidator(allowed_extensions=("mp4"))]

    class Meta:
        verbose_name = _("video file")
        verbose_name_plural = _("video files")

    def generate_video_thumbnail(self):
        """Generates video thumbnail (square proportion)"""

        # check if video file actually exists
        if self.file:
            # delete existing thumbnail file
            if self.thumbnail:
                self.thumbnail.delete(save=False)

            # generate new thumbnail
            video = self
            video_filename = os.path.splitext(video.file.name)[0]
            thumbnail_filename = os.path.split(video_filename)[1] + "_thumb.jpg"
            ffmpeg_tempfile = tempfile.NamedTemporaryFile()
            # video_thumbnail_output = '.' + settings.MEDIA_URL + thumbnail_filename
            size = (128, 128)

            if django_settings.USE_S3:
                # get video full S3 url path
                video_url = video.file.url
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
            self.thumbnail.save(
                name=thumbnail_filename, content=ffmpeg_tempfile, save=False
            )

            # calling save command, specifying that only the thumbnail field will be updated
            # this will be read by the @post_save signal receiver
            self.save(update_fields=["thumbnail"])

            # closes temporary file and allows it to be deleted
            ffmpeg_tempfile.close()

    def delete(self, *args, **kwargs):
        # Delete the actual video file
        self.file.delete(save=False)

        # Delete file from S3 storage (if uploaded without using django-storages)
        if self.s3_key:
            delete_file_from_s3(AWS_STORAGE_BUCKET_NAME, self.s3_key)

        # Delete thumbnail file
        if self.thumbnail:
            self.thumbnail.delete(save=False)

        # Delete subtitle file
        if self.subtitle:
            self.subtitle.delete(save=False)

        # Call the "real" delete() method.
        super().delete(*args, **kwargs)

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
