import os
import io
import tempfile
import logging
import ffmpeg

from django.db import models
from django.core.validators import FileExtensionValidator
from django.contrib.auth.models import User
# from django.core.files.uploadedfile import InMemoryUploadedFile

from PIL import Image

from courses.models import Course

# Get an instance of a logger
logger = logging.getLogger(__name__)


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'user_{0}/{1}'.format(instance.author.id, filename)


def read_frame_as_jpeg(in_filename, time):
    """extracts singlke frame from video based on a specific timestamp"""
    # based on: https://github.com/kkroening/ffmpeg-python/blob/master/examples/read_frame_as_jpeg.py
    out, err = (
        ffmpeg
        .input(in_filename, ss=time)
        # .filter('select', 'gte(n,{})'.format(frame_num))
        .output('pipe:', vframes=1, format='image2', vcodec='mjpeg')
        .run(capture_stdout=True)
    )
    return (out, err)


def crop_image(image):
    """Generates a square cropped image based on its center"""
    width, height = image.size

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


class VideoFile(models.Model):
    objects = VideoFileQuerySet.as_manager()
    related_name = 'videos'
    title = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=255)
    author = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name=related_name)
    course = models.ForeignKey(
        Course, on_delete=models.PROTECT, related_name=related_name)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to=user_directory_path)
    thumbnail = models.ImageField(
        upload_to=user_directory_path, blank=True, null=True)
    # forum = models.ForeignKey(
    #     Forum, on_delete=models.CASCADE, related_name='video')
    validators = [FileExtensionValidator(allowed_extensions=('mp4'))]

    def generate_video_thumbnail(self):
        """Generates video thumbnail (square proportion)"""
        video = self
        video_filename = os.path.splitext(video.file.name)[0]
        thumbnail_filename = os.path.split(video_filename)[1] + '_thumb.jpg'
        ffmpeg_tempfile = tempfile.NamedTemporaryFile()
        # video_thumbnail_output = '.' + settings.MEDIA_URL + thumbnail_filename
        size = (128, 128)

        (ffmpeg_output, ffmpeg_error) = read_frame_as_jpeg(
            video.file.path, '00:00:01.000')

        if ffmpeg_error is None:
            logger.info('Video thumbnail generated ok')
            thumbnail = Image.open(io.BytesIO(ffmpeg_output))
            thumbnail = crop_image(thumbnail)
            thumbnail.thumbnail(size)
            thumbnail.save(ffmpeg_tempfile, 'JPEG')
            ffmpeg_tempfile.seek(0)
            logger.info('Video thumbnail resized ok')
        else:
            logger.error('Error generating thumbnail')
            raise ValueError('Error generating thumbnail:' + ffmpeg_error)

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

    def __str__(self):
        return self.title
