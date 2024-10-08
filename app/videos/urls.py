from videos import views as video_views

from django.urls import path

urlpatterns = [
    path(
        "courses/<int:pk>/section/<int:section_pk>/upload/",
        video_views.upload_video,
        # video_views.UploadVideoView.as_view(),
        name="upload_video",
    ),
    path(
        "courses/<int:pk>/section/<int:section_pk>/signed-url/",
        video_views.SignedURLView.as_view(),
        name="signed_url",
    ),
    path(
        "courses/<int:pk>/section/<int:section_pk>/videos/<int:sectionitem_pk>/publish",
        video_views.publish_video,
        name="publish_video",
    ),
    path(
        "courses/<int:pk>/section/<int:section_pk>/videos/<int:sectionitem_pk>/unpublish",
        video_views.unpublish_video,
        name="unpublish_video",
    ),
    path(
        "courses/<int:pk>/section/<int:section_pk>/videos/<int:sectionitem_pk>/delete",
        video_views.delete_video,
        name="delete_video",
    ),
    path(
        "courses/<int:pk>/section/<int:section_pk>/videos/<int:sectionitem_pk>/",
        video_views.video_player,
        name="video_player",
    ),
]
