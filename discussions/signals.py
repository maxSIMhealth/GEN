# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from discussions.models import VideoFile


# @receiver(post_save, sender=VideoFile)
# def generate_thumbnail(sender, **kwargs):
#     # try to delete existing thumbnail
#     try:
#         # sender.thumbnail.delete()
#         kwargs['instance'].generate_thumbnail()
#     except:
#         pass
