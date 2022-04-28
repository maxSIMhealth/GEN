from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin
from modeltranslation.admin import TabbedTranslationAdmin, TranslationTabularInline

from django.contrib import admin

# from quiz.models import Quiz
from .forms import SectionAdminForm
from .models import Course, Section, SectionItem, Status


def duplicate(modeladmin, request, queryset):
    for item in queryset:
        item.duplicate(request=request)


duplicate.short_description = "Duplicate selected items"


class SectionInline(SortableInlineAdminMixin, TranslationTabularInline):
    model = Section
    exclude = [
        "description",
    ]
    extra = 0


class CourseAdmin(TabbedTranslationAdmin):
    # fields = ('name', 'members')
    list_display = ("name", "id", "code", "author", "enable_gamification")
    list_filter = ("author",)
    # ordering = ("id",)
    filter_horizontal = ("members", "instructors", "editors", "learners")
    actions = [duplicate]
    save_as = True
    inlines = (SectionInline,)
    readonly_fields = ["created", "modified"]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "author",
                    "code",
                    "show_code",
                    "type",
                    "initial_section_name",
                    "description",
                    "requirement",
                )
            },
        ),
        (
            "Additional information",
            {
                "fields": (
                    "created",
                    "modified",
                )
            },
        ),
        (
            "Date settings",
            {
                "fields": (
                    "start_date",
                    "end_date",
                )
            },
        ),
        (
            "Participants",
            {
                "fields": (
                    "auto_enroll",
                    "blind_data",
                    "members",
                    "learners",
                    "learners_max_number",
                    "instructors",
                    "editors",
                )
            },
        ),
        (
            "Certificate",
            {
                "fields": (
                    "certificate_type",
                    "certificate_custom_term",
                    "certificate_template",
                )
            },
        ),
        (
            "Gamification",
            {
                "fields": (
                    "enable_gamification",
                    "show_scoreboard",
                    "show_leaderboard",
                    "show_progress_tracker",
                )
            },
        ),
    )


class SectionItemInline(SortableInlineAdminMixin, TranslationTabularInline):
    model = SectionItem
    exclude = ["author", "start_date", "end_date", "description"]
    extra = 0


class SectionAdmin(SortableAdminMixin, TabbedTranslationAdmin):
    list_display = (
        "name",
        "published",
        "course",
        "access_restriction",
        "author",
    )
    inlines = (SectionItemInline,)
    list_filter = ("course", "published", "access_restriction")
    form = SectionAdminForm
    readonly_fields = ["created", "modified"]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "description",
                    "course",
                    "section_type",
                    "author",
                    "start_date",
                    "end_date",
                    "requirement",
                    "published",
                    "completion_message",
                )
            },
        ),
        (
            "Additional information",
            {
                "fields": (
                    "created",
                    "modified",
                )
            },
        ),
        (
            "Layout",
            {
                "fields": (
                    "paginate",
                    "show_thumbnails",
                    "show_related_video_name",
                    "group_by_video",
                )
            },
        ),
        (
            "Access control",
            {
                "fields": (
                    "access_restriction",
                    "author_access_override",
                )
            },
        ),
        (
            "Assessment",
            {
                "fields": (
                    "pre_assessment",
                    "final_assessment",
                )
            },
        ),
        (
            "Output >> Discussion board",
            {
                "fields": (
                    "create_discussions",
                    "section_output",
                    "output_access_restriction",
                    "output_author_access_override",
                )
            },
        ),
        (
            "Output >> Quiz",
            {
                "fields": (
                    "clone_quiz",
                    "clone_quiz_reference",
                    "clone_quiz_output_section",
                    "clone_quiz_update_owner",
                )
            },
        ),
    )


class StatusAdmin(admin.ModelAdmin):
    list_display = (
        "learner",
        "course",
        "section",
        "completed",
    )
    list_filter = ("course", "section", "learner")
    readonly_fields = ["created", "modified"]


admin.site.register(Course, CourseAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(Status, StatusAdmin)
