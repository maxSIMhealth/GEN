from accounts.serializers import UserSerializer
from api.permissions import IsAdminOrReadOnly, IsAuthorOrAdmin
from courses.models import Course, Section, SectionItem
from courses.serializers import (
    CourseSerializer,
    CoursesSerializer,
    SectionDetailSerializer,
    SectionItemSerializer,
    VideoFileSerializer,
)
from rest_framework import generics, status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from videos.models import VideoFile

from django.contrib.auth.models import User


# App: accounts (user and profile data)
class UserRecordView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, format=None):
        user = self.request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)


class UsersRecordView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, format=None):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=ValueError):
            serializer.create(validated_data=request.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            {"error": True, "error_msg": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


# App: Courses
# class CourseApiViewSet(viewsets.ModelViewSet):
#     queryset = Course.objects.all()
#     serializer_class = CourseSerializer


class CourseListApiView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    # queryset = Course.objects.all()
    serializer_class = CoursesSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = user.member.all()
        return queryset


class CourseDetailApiView(generics.RetrieveAPIView):
    # queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = user.member.all()
        return queryset


class SectionDetailApiView(generics.RetrieveUpdateAPIView):
    # queryset = Section.objects.all()
    serializer_class = SectionDetailSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        queryset = Section.objects.exclude(published=False)
        return queryset


class SectionItemDetailApiView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SectionItem.objects.all()
    serializer_class = SectionItemSerializer
    permission_classes = [IsAuthorOrAdmin]


class UploadVideoApiView(generics.ListCreateAPIView):
    # queryset = VideoFile.objects.all()
    serializer_class = VideoFileSerializer

    def get_queryset(self):
        section_pk = self.kwargs["section_pk"]
        try:
            # getting videos authored by the current user for a specific section.
            queryset = VideoFile.objects.filter(
                section=section_pk, author=self.request.user
            )
        except VideoFile.DoesNotExist:
            queryset = None
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # check if an upload already exists

        # additional required parameter
        course_pk = kwargs["course_pk"]
        section_pk = kwargs["section_pk"]
        course_obj = Course.objects.get(pk=course_pk)
        section_obj = Section.objects.get(pk=section_pk)
        author = request.user
        name = "Video upload"

        # save object
        serializer.save(
            author=author, section=section_obj, course=course_obj, name=name
        )
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


# class PublishVideoApiView(mixins.UpdateModelMixin, generics.GenericAPIView):
#     def patch(self, request, *args, **kwargs):
#         return self.partial_update(request, *args, **kwargs)


# class SectionApiViewSet(viewsets.ModelViewSet):
#     queryset = Section.objects.all()
#     serializer_class = SectionSerializer
#
#     def get_queryset(self):
#         queryset = Section.objects.exclude(published=False)
#         return queryset


# class SectionViewSet(mixins.ListModelMixin,
#                      mixins.RetrieveModelMixin,
#                      viewsets.GenericViewSet):
#     queryset = Section.objects.all()
#     serializer_class = SectionSerializer
#
#     def list(self, request, course_pk=None, pk=None):
#         queryset = Section.objects.filter(course=course_pk)
#         serializer = SectionSerializer(queryset)
#         return Response(serializer.data)

#
# @api_view(["GET", "POST"])
# def get_course(request, pk):
#     course = Course.objects.get(id=pk)
#     serializer = CourseSerializer(course, many=False)
#
#     return Response(serializer.data)
