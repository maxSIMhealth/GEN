from rest_framework import serializers
from videos.models import VideoFile

from .models import Course, Section, SectionItem

# class UploadSectionItemSerializer(serializers.ModelSerializer):
#     type = serializers.SerializerMethodField('get_item_type')
#
#     def get_item_type(self, obj):
#         return obj.item_type
#
#     class Meta:
#         model = SectionItem
#         fields = [
#             "id",
#             "name",
#             "description",
#             "published",
#             "type"
#         ]


class VideoFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoFile
        fields = [
            # "published",
            "file",
            "thumbnail",
        ]


class SectionItemSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField("get_item_type")
    video = VideoFileSerializer(source="videofile")

    def get_item_type(self, obj):
        return obj.item_type

    class Meta:
        model = SectionItem
        fields = ["id", "name", "description", "published", "type", "video"]


class FilteredSectionListSerializer(serializers.ListSerializer):
    """
    Filtering Section List to show only items set as published.
    """

    def update(self, instance, validated_data):
        pass

    def to_representation(self, data):
        data = data.filter(published=True)
        return super(FilteredSectionListSerializer, self).to_representation(data)


class SectionSerializer(serializers.ModelSerializer):
    # items = SectionItemSerializer(many=True, read_only=True, source="section_items")
    type = serializers.SerializerMethodField("get_section_type")

    def get_section_type(self, item):
        return item.section_type

    class Meta:
        model = Section
        list_serializer_class = FilteredSectionListSerializer
        fields = [
            "id",
            "name",
            "description",
            "type",
            "published",
            # "items",
        ]


class SectionDetailSerializer(serializers.ModelSerializer):
    items = SectionItemSerializer(many=True, read_only=True, source="section_items")
    type = serializers.SerializerMethodField("get_section_type")

    def get_section_type(self, item):
        return item.section_type

    class Meta:
        model = Section
        list_serializer_class = FilteredSectionListSerializer
        fields = [
            "id",
            "name",
            "description",
            "type",
            "published",
            "items",
        ]


class CourseSerializer(serializers.ModelSerializer):
    sections = SectionSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = [
            "id",
            "name",
            "code",
            "type",
            "author",
            "description",
            "sections",
        ]


class CoursesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            "id",
            "name",
            "code",
            "type",
            "author",
            "description",
        ]
