from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin
from django.contrib import admin

# from quiz.models import Quiz
from .models import Course, Section, SectionItem


class CourseAdmin(admin.ModelAdmin):
    # fields = ('name', 'students')
    list_display = ("name", "code", "author", "enable_gamification")
    list_filter = ("author",)
    filter_horizontal = ("students", "instructors")
    save_as = True


class SectionInline(SortableInlineAdminMixin, admin.TabularInline):
    model = SectionItem
    extra = 0


class SectionAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = (
        "name",
        "course",
    )
    inlines = (SectionInline,)


admin.site.register(Course, CourseAdmin)
admin.site.register(Section, SectionAdmin)
