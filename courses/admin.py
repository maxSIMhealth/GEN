from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin
from django.contrib import admin
from modeltranslation.admin import TabbedTranslationAdmin, TranslationTabularInline

# from quiz.models import Quiz
from .forms import SectionAdminForm
from .models import Course, Section, SectionItem


class SectionInline(SortableInlineAdminMixin, TranslationTabularInline):
    model = Section
    exclude = ["description", "content"]
    extra = 0


class CourseAdmin(TabbedTranslationAdmin):
    # fields = ('name', 'students')
    list_display = ("name", "code", "author", "enable_gamification")
    list_filter = ("author",)
    filter_horizontal = ("students", "instructors", "participants")
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


admin.site.register(Course, CourseAdmin)
admin.site.register(Section, SectionAdmin)
