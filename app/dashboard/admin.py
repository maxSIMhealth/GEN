from django.contrib import admin
from modeltranslation.admin import TabbedTranslationAdmin

from .models import DashboardSettings

class DashboardAdmin(TabbedTranslationAdmin):
    list_display = (
        "name",
        "active"
    )


admin.site.register(DashboardSettings, DashboardAdmin)