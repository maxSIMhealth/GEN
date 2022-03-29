from django.contrib import admin
from modeltranslation.admin import TabbedTranslationAdmin

from .models import ContentItem, ImageFile, PdfFile


class ContentItemAdmin(TabbedTranslationAdmin):
    list_filter = ("published", "section__course", "section", )
    list_display = (
        "id",
        "name",
        "section",
    )
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
                    "content"
                )
            },
        ),
    )


class ImageFileAdmin(TabbedTranslationAdmin):
    list_filter = ("published", "section__course", "section", "author", )
    list_display = ("id", "name", "section", )
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
    )


class PdfFileAdmin(TabbedTranslationAdmin):
    list_filter = ("published", "section__course", "section", )
    list_display = (
        "id",
        "name",
        "section",
    )
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
    )


admin.site.register(ContentItem, ContentItemAdmin)
admin.site.register(ImageFile, ImageFileAdmin)
admin.site.register(PdfFile, PdfFileAdmin)
