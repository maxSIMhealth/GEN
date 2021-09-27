from django.urls import path

from quiz import views as quiz_views

urlpatterns = (
    path(
        "courses/<int:pk>/section/<int:section_pk>/quiz/<int:sectionitem_pk>/",
        quiz_views.quiz_page,
        name="quiz",
    ),
    path(
        "courses/<int:pk>/section/<int:section_pk>/quiz/<int:sectionitem_pk>/result/",
        quiz_views.quiz_result,
        name="quiz_result",
    ),
    path(
        "courses/<int:pk>/section/<int:section_pk>/quiz/<int:sectionitem_pk>/result_list/",
        quiz_views.QuestionAttemptListViewAlt.as_view(),
        name="quiz_result_list",
    ),
)
