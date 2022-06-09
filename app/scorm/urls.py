from scorm import views

from django.urls import path

urlpatterns = (
    path(
        "courses/<int:pk>/section/<int:section_pk>/scorm/<int:scorm_object_pk>/exit_redirect",
        views.scorm_exit_redirect,
        name="scorm_exit_redirect",
    ),
)
