from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import VideoFile


# @receiver(post_save, sender=VideoFile)
# def generate_thumbnail(sender, instance, created, **kwargs):
#     """
#     Receiver that will call the `generate_video_thumbnail` function
#     when a new video file object is created.
#     """
#
#     # TODO: make this receiver also work when a video object is updated.
#     # It is a bit tricky because other actions (like delete) also send a post_save signal.
#     #
#     # If `save` is called with `thumbnail` in the `update_fields`
#     #     field, it means that it was called by the `generate_video_thumbnail` function.
#     # try:
#     #     updated_thumbnail = kwargs["update_fields"].__contains__("thumbnail")
#     # except AttributeError:
#     #     updated_thumbnail = False
#
#     if created:
#         instance.generate_video_thumbnail()
