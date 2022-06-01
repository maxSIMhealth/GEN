from courses.models import Section
from modeltranslation.admin import TabbedTranslationAdmin

from django.contrib import admin
from django.http import HttpResponseRedirect
from django.utils.html import format_html

from .models import ContentItem, ExternalObject, ImageFile, PdfFile


def refresh(modeladmin, request, queryset):
    for item in queryset:
        item.save()


refresh.short_description = "Refresh selected items (update content type)"


def duplicate(modeladmin, request, queryset):
    for item in queryset:
        item.duplicate(suffix="(copy)", published=False)


duplicate.short_description = "Duplicate selected items"


def duplicate_with_file(modeladmin, request, queryset):
    for item in queryset:
        item.duplicate(suffix="(copy)", published=False, file=True)


duplicate_with_file.short_description = "Duplicate selected items"


def unzip_file(modeladmin, request, queryset):
    for item in queryset:
        item.unzip_package(request)


unzip_file.short_description = "Extract zip file(s)"


class ContentItemAdmin(TabbedTranslationAdmin):
    list_filter = (
        "published",
        "section__course",
        "section",
    )
    list_display = (
        "name",
        "item_type",
        "id",
        "section",
    )
    actions = [duplicate, refresh]
    readonly_fields = ["created", "modified"]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "author",
                    "start_date",
                    "end_date",
                    "section",
                    "published",
                    "description",
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
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Sorting 'section' field based on Course ID and Section ID.
        """
        if db_field.name == "section":
            kwargs["queryset"] = Section.objects.all().order_by("course_id", "id")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class ImageFileAdmin(TabbedTranslationAdmin):
    list_filter = (
        "published",
        "section__course",
        "section",
        "author",
    )
    list_display = ("name", "item_type", "id", "section", "file", "published")
    readonly_fields = ["created", "modified"]
    actions = [duplicate_with_file, refresh]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "author",
                    "file",
                    "published",
                    "description",
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
    )


class PdfFileAdmin(TabbedTranslationAdmin):
    list_filter = (
        "published",
        "section__course",
        "section",
    )
    list_display = (
        "name",
        "item_type",
        "id",
        "section",
        "file",
        "published",
    )
    readonly_fields = ["created", "modified"]
    actions = [duplicate_with_file, refresh]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "author",
                    "section",
                    "published",
                    "file",
                    "description",
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
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Sorting 'section' field based on Course ID and Section ID.
        """
        if db_field.name == "section":
            kwargs["queryset"] = Section.objects.all().order_by("course_id", "id")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class ExternalObjectAdmin(TabbedTranslationAdmin):
    list_filter = (
        "published",
        "section__course",
        "section",
        "author",
    )
    list_display = ("name", "item_type", "id", "section", "file", "published")
    readonly_fields = ["created", "modified", "directory", "url_clickable"]
    actions = [duplicate_with_file, refresh, unzip_file]
    change_form_template = "admin/external_object_form.html"
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "author",
                    "file",
                    "section",
                    "published",
                    "description",
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
            "Zip File Data",
            {
                "fields": (
                    "directory",
                    "url_clickable",
                )
            },
        ),
    )

    def response_change(self, request, obj):
        if "_extract_zip" in request.POST:
            obj.unzip_package(request)
            # self.message_user(request, "Zip file extracted.")
            return HttpResponseRedirect(".")

        return super().response_change(request, obj)

    def url_clickable(self, instance):
        return format_html(
            f"<a href='{instance.url}' target='_blank'>{instance.url}</a>"
        )

    url_clickable.short_description = "URL"


admin.site.register(ContentItem, ContentItemAdmin)
admin.site.register(ImageFile, ImageFileAdmin)
admin.site.register(PdfFile, PdfFileAdmin)
admin.site.register(ExternalObject, ExternalObjectAdmin)
