from modeltranslation.admin import TabbedTranslationAdmin

from django.contrib import admin

from .models import DashboardSetting


class DashboardAdmin(TabbedTranslationAdmin):
    list_display = ("name", "active", "created", "modified")
    readonly_fields = ["created", "modified"]


admin.site.register(DashboardSetting, DashboardAdmin)
