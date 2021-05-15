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
    filter_horizontal = ("members", "instructors", "learners")
    save_as = True

    inlines = (SectionInline,)


class SectionItemInline(SortableInlineAdminMixin, TranslationTabularInline):
    model = SectionItem
    exclude = ["author", "start_date", "end_date", "description"]
    extra = 0


class SectionAdmin(SortableAdminMixin, TabbedTranslationAdmin):
    list_display = (
        "name",
        "course",
    )
    inlines = (SectionItemInline,)
    list_filter = ("course",)
    form = SectionAdminForm

class StatusAdmin(admin.ModelAdmin):
    list_display = (
        "course",
        "section",
        "completed"
    )
    # list_filter = ("")

admin.site.register(Course, CourseAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(Status, StatusAdmin)
