from django.contrib import admin

from .models import Course, MediaFile, Forum, Comment


class CourseAdmin(admin.ModelAdmin):
    # fields = ('name', 'students')
    filter_horizontal = ('students',)


admin.site.register(Course, CourseAdmin)
admin.site.register(MediaFile)
admin.site.register(Forum)
admin.site.register(Comment)
