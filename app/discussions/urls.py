from django.urls import path

from discussions import views as discussion_views

urlpatterns = [
    path(
        "courses/<int:pk>/section/<int:section_pk>/discussion/new/",
        discussion_views.new_discussion,
        name="new_discussion",
    ),
    path(
        "courses/<int:pk>/section/<int:section_pk>/discussion/<int:sectionitem_pk>/",
        discussion_views.discussion_comments,
        name="discussion_comments",
    ),
    path(
        "courses/<int:pk>/section/<int:section_pk>/discussion/<int:sectionitem_pk>/vote/add/",
        discussion_views.add_discussion_vote,
        name="discussion_add_vote",
    ),
    path(
        "courses/<int:pk>/section/<int:section_pk>/discussion/<int:sectionitem_pk>/vote/clear/",
        discussion_views.remove_discussion_vote,
        name="discussion_remove_vote",
    ),
    path(
        "courses/<int:pk>/section/<int:section_pk>/discussion/<int:sectionitem_pk>/comment/<int:comment_pk>/vote/add/",
        discussion_views.add_comment_vote,
        name="comment_add_vote",
    ),
    path(
        "courses/<int:pk>/section/<int:section_pk>/discussion/<int:sectionitem_pk>/comment/<int:comment_pk>/vote/remove/",
        discussion_views.remove_comment_vote,
        name="comment_remove_vote",
    ),
]