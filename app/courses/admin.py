from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin
from django.contrib import admin
from modeltranslation.admin import TabbedTranslationAdmin, TranslationTabularInline

# from quiz.models import Quiz
from .forms import SectionAdminForm
from .models import Course, Section, SectionItem, Status


class SectionInline(SortableInlineAdminMixin, TranslationTabularInline):
    model = Section
    exclude = ["description", "content"]
    extra = 0


class CourseAdmin(TabbedTranslationAdmin):
    # fields = ('name', 'members')
    list_display = ("name", "code", "author", "enable_gamification")
    list_filter = ("author",)
    filter_horizontal = ("members", "instructors", "editors", "learners")
    save_as = True

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
                    "description",
                    "requirement",
                    "blind_data",
                )
            }
        ),
        (
            "Date settings",
            {
                "fields": (
                    "start_date",
                    "end_date",
                )
            }
        ),
        (
            "Participants",
            {
                "fields": (
                    "members",
                    "learners",
                    "learners_max_number",
                    "instructors",
                    "editors",
                )
            }
        ),
        (
            "Certificate",
            {
                "fields": (
                    "certificate_type",
                    "certificate_custom_term",
                    "certificate_template",
                )
            }
        ),
        (
            "Gamification",
            {
                "fields": (
                    "enable_gamification",
                    "show_scoreboard",
                    "show_leaderboard",
                    "show_progress_tracker"
                )
            }
        )
    )

    inlines = (SectionInline,)


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

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "description",
                    "content",
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
            "Layout",
            {
                "fields": (
                    "paginate",
                    "show_thumbnails",
                    "show_related_video_name",
                    "group_by_video",
                )
            }
        ),
        (
            "Access control",
            {
                "fields": (
                    "access_restriction",
                    "author_access_override",
                )
            }
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
                    "output_author_access_override"
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
                    "clone_quiz_update_owner"
                )
            }
        )
    )


class StatusAdmin(admin.ModelAdmin):
    list_display = (
        "learner",
        "course",
        "section",
        "completed"
    )
    list_filter = ("course","section","learner")


admin.site.register(Course, CourseAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(Status, StatusAdmin)
