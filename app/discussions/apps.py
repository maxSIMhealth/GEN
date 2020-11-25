from django.apps import AppConfig


class DiscussionsConfig(AppConfig):
    name = "discussions"

    def ready(self):
        import discussions.signals

        return super().ready()
