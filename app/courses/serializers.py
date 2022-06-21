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
    # author_id = serializers.StringRelatedField(
    #     default=serializers.CurrentUserDefault(),
    #     read_only=True
    # )

    class Meta:
        model = VideoFile
        fields = [
            # "author",
            # "course",
            # "section",
            "name",
            "published",
            "file",
            "thumbnail",
        ]
        read_only_fields = [
            "name",
            "published",
            "thumbnail",
        ]

    # def validate(self, attrs):
    #     author = attrs.get("author")
    #     if author != self.request.user:

    # def validate_author(self, value):
    #     if value != self.request.user:
    #         raise serializers.ValidationError("Author must be the current user.")


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
    # items = SectionItemSerializer(many=True, read_only=True, source="section_items")
    type = serializers.SerializerMethodField("get_section_type")
    items = serializers.SerializerMethodField("get_filtered_items")

    def _user(self):
        request = self.context["request"]
        if request:
            return request.user

    def get_section_type(self, item):
        return item.section_type

    def get_filtered_items(self, item):
        # filtering items queryset to show only items authored by the current user.
        items_queryset = SectionItem.objects.filter(author=self._user())
        serializer = SectionItemSerializer(
            instance=items_queryset, many=True, context=self.context
        )
        return serializer.data

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
