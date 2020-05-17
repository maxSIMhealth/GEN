from django.contrib import admin

from .models import Course


class CourseAdmin(admin.ModelAdmin):
    # fields = ('name', 'students')
    list_display = ("name", "code", "author", "enable_gamification")
    list_filter = ("author",)
    filter_horizontal = ("students", "instructors")
    save_as = True


admin.site.register(Course, CourseAdmin)
