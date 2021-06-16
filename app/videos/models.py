import io
import logging
import os
import tempfile
import uuid

# from django.core.validators import FileExtensionValidator
from django.core.files.storage import get_storage_class
from django.db import models
from django.utils.translation import gettext_lazy as _
import ffmpeg
from GEN.support_methods import duplicate_item, duplicate_name
from GEN import settings as django_settings
from PIL import Image
from tinymce.models import HTMLField
from upload_validator import FileTypeValidator

from courses.models import Course, SectionItem

# from django.core.files.uploadedfile import InMemoryUploadedFile

# Get an instance of a logger
logger = logging.getLogger(__name__)

# Media storage object to be able to obtain media full url
media_storage = get_storage_class()()


def user_directory_path(instance, filename):
    ext = filename.split(".")[-1]
    random_filename = str(uuid.uuid4().hex)
    filename = "%s.%s" % (random_filename, ext)
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return "user_{0}/{1}".format(instance.author.id, filename)


def read_frame_as_jpeg(in_filename, time):
    """extracts single frame from video based on a specific timestamp"""
    # based on:
    # https://github.com/kkroening/ffmpeg-python/blob/master/examples/read_frame_as_jpeg.py
    out, err = (
        ffmpeg.input(in_filename, ss=time)
        # .filter('select', 'gte(n,{})'.format(frame_num))
        .output("pipe:", vframes=1, format="image2", vcodec="mjpeg").run(
            capture_stdout=True
        )
    )
    return out, err


def crop_image(image):
    """Generates a square cropped image based on its center"""
    width, height = image.size
    left, top, right, bottom = 0, 0, 0, 0

    if width != height:
        if width > height:
            crop = (width - height) / 2
            left = crop
            top = 0
            right = height + crop
            bottom = height
        elif width < height:
            crop = (height - width) / 2
            left = 0
            top = crop
            right = width
            bottom = width + crop

        result = image.crop((left, top, right, bottom))
    else:
        result = image

    return result


class VideoFileQuerySet(models.QuerySet):
    def delete(self, *args, **kwargs):
        for obj in self:
            obj.file.delete()
            obj.thumbnail.delete()
        super().delete(*args, **kwargs)


class Playlist(SectionItem):
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
        validators=[FileTypeValidator(allowed_types=["text/plain",])],
    )
    internal_name = models.CharField(
        _("internal name"),
        max_length=255,
        null=True,
        blank=True,
        help_text=_("video internal name (not visible to users)"),
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

        # save thumbnail file in user directory and link it to video object
        self.thumbnail.save(thumbnail_filename, ffmpeg_tempfile)

        # closes temporary file and allows it to be deleted
        ffmpeg_tempfile.close()

    def delete(self, *args, **kwargs):
        self.file.delete()  # Delete the actual video file
        self.thumbnail.delete()  # Delete the thumbnail file
        super().delete(*args, **kwargs)  # Call the "real" delete() method.

    def duplicate(self):
        return duplicate_item(self, callback=duplicate_name)


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
