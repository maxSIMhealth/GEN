from django.contrib import admin

from .models import Course


class CourseAdmin(admin.ModelAdmin):
    # fields = ('name', 'students')
    filter_horizontal = ('students', 'instructors')
    save_as = True


admin.site.register(Course, CourseAdmin)
