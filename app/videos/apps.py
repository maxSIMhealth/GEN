from django.apps import AppConfig


class VideosConfig(AppConfig):
    name = "videos"

    def ready(self):
        from . import signals  # noqa: F401
