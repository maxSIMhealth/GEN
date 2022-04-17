from django.apps import AppConfig
from django.db.models.signals import post_save


class VideosConfig(AppConfig):
    name = "videos"

    def ready(self):
        from videos import signals

        post_save.connect(signals.generate_thumbnail)
