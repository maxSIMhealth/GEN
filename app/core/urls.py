from core.views import HelpPageView

from django.urls import path

urlpatterns = (
    path(
        "help/",
        HelpPageView.as_view(),
        name="help",
    ),
)
