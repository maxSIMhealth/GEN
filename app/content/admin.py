from django.contrib import admin
from modeltranslation.admin import TabbedTranslationAdmin

from .models import ContentItem, MatchColumnsGame, MatchColumnsItem


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


class MatchColumnsGameAdmin(TabbedTranslationAdmin):
    list_filter = ("published", "section__course", "section",)
    list_display = (
        "id",
        "name",
        "section",
    )
    filter_horizontal = ("source_column_items", "choice1_column_items", "choice2_column_items")


class MatchColumnsItemAdmin(TabbedTranslationAdmin):
    list_filter = ("name", )
    list_display = ("id", "name")


admin.site.register(ContentItem, ContentItemAdmin)
admin.site.register(MatchColumnsGame, MatchColumnsGameAdmin)
admin.site.register(MatchColumnsItem, MatchColumnsItemAdmin)
