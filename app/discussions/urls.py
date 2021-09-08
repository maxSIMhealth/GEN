from django.urls import path

from discussions import views as discussion_views

urlpatterns = [
    path(
        "courses/<int:pk>/section/<int:section_pk>/discussion/new/",
        discussion_views.new_discussion,
        name="new_discussion",
    ),
    path(
        "courses/<int:pk>/section/<int:section_pk>/discussion/<int:discussion_pk>/",
        discussion_views.discussion_comments,
        name="discussion_comments",
    ),
    path(
        "courses/<int:pk>/section/<int:section_pk>/discussion/<int:discussion_pk>/upvote/",
        discussion_views.upvote_discussion,
        name="discussion_upvote",
    ),
    path(
        "courses/<int:pk>/section/<int:section_pk>/discussion/<int:discussion_pk>/clearvote/",
        discussion_views.clearvote_discussion,
        name="discussion_clearvote",
    ),
    path(
        "courses/<int:pk>/section/<int:section_pk>/discussion/<int:discussion_pk>/comment/<int:comment_pk>/upvote/",
        discussion_views.upvote_comment,
        name="comment_upvote",
    ),
    path(
        "courses/<int:pk>/section/<int:section_pk>/discussion/<int:discussion_pk>/comment/<int:comment_pk>/clearvote/",
        discussion_views.clearvote_comment,
        name="comment_clearvote",
    ),
]