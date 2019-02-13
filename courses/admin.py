from django.contrib import admin

from .models import Course


class CourseAdmin(admin.ModelAdmin):
    # fields = ('name', 'students')
    filter_horizontal = ('students',)


admin.site.register(Course, CourseAdmin)
