from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin
from django.contrib import admin
from modeltranslation.admin import TranslationAdmin, TranslationTabularInline

# from quiz.models import Quiz
from .forms import SectionAdminForm
from .models import Course, Section, SectionItem


class SectionInline(SortableInlineAdminMixin, TranslationTabularInline):
    model = Section
    exclude = ["description"]
    extra = 0


class CourseAdmin(TranslationAdmin):
    # fields = ('name', 'students')
    list_display = ("name", "code", "author", "enable_gamification")
    list_filter = ("author",)
    filter_horizontal = ("students", "instructors")
    save_as = True

    inlines = (SectionInline,)


class SectionItemInline(SortableInlineAdminMixin, TranslationTabularInline):
    model = SectionItem
    exclude = ["author", "start_date", "end_date", "description"]
    extra = 0


class SectionAdmin(SortableAdminMixin, TranslationAdmin):
    list_display = (
        "name",
        "course",
    )
    inlines = (SectionItemInline,)
    list_filter = ("course",)
    form = SectionAdminForm


admin.site.register(Course, CourseAdmin)
admin.site.register(Section, SectionAdmin)
