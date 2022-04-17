from courses import views as course_views

from django.urls import path
from django.views.generic.base import RedirectView

urlpatterns = [
    path("courses/", RedirectView.as_view(url="/"), name="courses"),
    path("courses/<int:pk>/", course_views.course, name="course"),
    path(
        "courses/<int:pk>/section/<int:section_pk>/",
        course_views.section_page,
        name="section",
    ),
    # certificate
    path(
        "courses/<int:pk>/certificate",
        course_views.generate_certificate,
        name="course_certificate",
    ),
    # tests / WIP
    # FIXME: list_pdfs has to be reimplemented
    # path('courses/<int:pk>/pdfs/', views.list_pdfs, name='list_pdfs'),
]
