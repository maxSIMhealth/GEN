import hashlib
import os

from urllib.parse import urlencode

from django import template
from django.conf import settings
from forums.models import VideoFile

register = template.Library()


@register.filter
def video_thumbnail(video_url):
    # video = VideoFile.objects.get(video)
    video_filename = os.path.splitext(video_url)[0]
    video_thumbnail = video_filename + '_thumb.jpg'
    # url = 'https://www.gravatar.com/avatar/{md5}?{params}'.format(
    #     md5=hashlib.md5(email).hexdigest(),
    #     params=urlencode({'d': default, 's': str(size)})
    # )
    return video_thumbnail
