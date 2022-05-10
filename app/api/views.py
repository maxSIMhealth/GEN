from accounts.serializers import UserSerializer
from courses.models import Course, Section, SectionItem
from courses.serializers import (
    CourseSerializer,
    CoursesSerializer,
    SectionDetailSerializer,
    SectionItemSerializer,
)
from rest_framework import generics, status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from django.contrib.auth.models import User


# App: accounts (user and profile data)
class UserRecordView(APIView):
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
    # permission_classes = [IsAuthenticated]
    queryset = Course.objects.all()
    serializer_class = CoursesSerializer


class CourseDetailApiView(generics.RetrieveAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer


class SectionDetailApiView(generics.RetrieveUpdateAPIView):
    queryset = Section.objects.all()
    serializer_class = SectionDetailSerializer

    def get_queryset(self):
        queryset = Section.objects.exclude(published=False)
        return queryset


class SectionItemDetailApiView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SectionItem.objects.all()
    serializer_class = SectionItemSerializer


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
