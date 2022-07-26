from adminsortable2.admin import SortableAdminMixin
from core.models import (
    CertificateFrameFile,
    CertificateLogoFile,
    CertificateTemplate,
    FooterLogoFile,
    HelpFaq,
    LoginAlertMessage,
)
from import_export import resources
from import_export.admin import ExportActionMixin, ImportExportMixin
from modeltranslation.admin import TabbedTranslationAdmin

from django.contrib import admin


class CertificateTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "created", "modified")
    readonly_fields = ["created", "modified"]


class CertificateLogoFileAdmin(admin.ModelAdmin):
    list_display = ("id", "file", "created", "modified")
    readonly_fields = ["created", "modified"]


class CertificateFrameFileAdmin(admin.ModelAdmin):
    list_display = ("id", "file", "created", "modified")
    readonly_fields = ["created", "modified"]


class FooterLogoFileAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ("id", "file", "created", "modified")
    readonly_fields = ["created", "modified"]
    extra = 0


class LoginAlertMessageAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = (
        "name",
        "published",
        "start_date",
        "end_date",
        "created",
        "modified",
    )
    readonly_fields = ["created", "modified"]


class HelpFaqResource(resources.ModelResource):
    class Meta:
        model = HelpFaq
        fields = ("id", "question", "answer")


class HelpFaqAdmin(
    SortableAdminMixin, ImportExportMixin, ExportActionMixin, TabbedTranslationAdmin
):
    list_display = ("question", "answer")
    exclude = ["custom_order"]
    readonly_fields = ["created", "modified"]
    resource_class = HelpFaqResource


admin.site.register(CertificateTemplate, CertificateTemplateAdmin)
admin.site.register(CertificateLogoFile, CertificateLogoFileAdmin)
admin.site.register(CertificateFrameFile, CertificateFrameFileAdmin)
admin.site.register(FooterLogoFile, FooterLogoFileAdmin)
admin.site.register(LoginAlertMessage, LoginAlertMessageAdmin)
admin.site.register(HelpFaq, HelpFaqAdmin)
