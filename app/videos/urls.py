from django.urls import path

from videos import views as video_views

urlpatterns = [
    path(
        "courses/<int:pk>/section/<int:section_pk>/upload/",
        video_views.upload_video,
        name="upload_video",
    ),
    path(
        "courses/<int:pk>/section/<int:section_pk>/videos/<int:video_pk>/publish",
        video_views.publish_video,
        name="publish_video",
    ),
    path(
        "courses/<int:pk>/section/<int:section_pk>/videos/<int:video_pk>/unpublish",
        video_views.unpublish_video,
        name="unpublish_video",
    ),
    path(
        "courses/<int:pk>/section/<int:section_pk>/videos/<int:video_pk>/delete",
        video_views.delete_video,
        name="delete_video",
    ),
    path(
        "courses/<int:pk>/section/<int:section_pk>/videos/<int:video_pk>/",
        video_views.video_player,
        name="video_player",
    ),
]