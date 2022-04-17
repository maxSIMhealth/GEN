from django.contrib import admin
from modeltranslation.admin import TabbedTranslationAdmin

from .models import ContentItem, ImageFile, PdfFile


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


class ContentItemAdmin(TabbedTranslationAdmin):
    list_filter = ("published", "section__course", "section", )
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
                    "content",
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
            }
        ),
    )


class ImageFileAdmin(TabbedTranslationAdmin):
    list_filter = (
        "published",
        "section__course",
        "section",
        "author",
    )
    list_display = (
        "name",
        "item_type",
        "id",
        "section",
        "file",
        "published"
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
            }
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
                    "content"
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
            }
        ),
    )


admin.site.register(ContentItem, ContentItemAdmin)
admin.site.register(ImageFile, ImageFileAdmin)
admin.site.register(PdfFile, PdfFileAdmin)
