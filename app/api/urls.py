from rest_framework import routers

from django.urls import include, path

from .views import (
    CourseDetailApiView,
    CourseListApiView,
    SectionDetailApiView,
    SectionItemDetailApiView,
    UploadVideoApiView,
    UserRecordView,
    UsersRecordView,
)

app_name = "api"

# Registering API routes
router = routers.DefaultRouter(trailing_slash=False)
# router.register('courses', CourseApiViewSet)
# router.register('sections', SectionApiViewSet)
# router.register('sections_test', SectionViewSet)
# router.register('user', UserRecordView.as_view(), basename="user")

urlpatterns = [
    # path("api/user/", UserRecordView.as_view(), name="user-record"),
    path("", include(router.urls)),
    path("profile/", UserRecordView.as_view(), name="profile"),
    path("users/", UsersRecordView.as_view(), name="users"),
    path("courses/", CourseListApiView.as_view(), name="course-list"),
    path("courses/<int:pk>/", CourseDetailApiView.as_view(), name="course-detail"),
    path(
        "courses/<int:course_pk>/section/<int:pk>/",
        SectionDetailApiView.as_view(),
        name="section-detail",
    ),
    path(
        "courses/<int:course_pk>/section/<int:section_pk>/item/<int:pk>/",
        SectionItemDetailApiView.as_view(),
        name="section-item-detail",
    ),
    path(
        "courses/<int:course_pk>/section/<int:section_pk>/upload/",
        UploadVideoApiView.as_view(),
        name="upload-video",
    ),
]
