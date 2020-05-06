from django.db.models.signals import pre_save
from django.dispatch import receiver
from forums.models import VideoFile


# @receiver(pre_save, sender=VideoFile)
# def delete_thumbnail(sender, **kwargs):
#     # try to delete existing thumbnail
#     try:
#         sender.thumbnail.delete()
#     except:
#         pass
