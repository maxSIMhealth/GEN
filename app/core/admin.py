from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin

from core.models import CertificateLogoFile, FooterLogoFile, CertificateTemplate, CertificateFrameFile, LoginAlertMessage


class CertificateTemplateAdmin(admin.ModelAdmin):
    list_display = (
        "name",
    )
    filter_horizontal = ("logos",)


class CertificateLogoFileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "file"
    )


class CertificateFrameFileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "file"
    )


class FooterLogoFileAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = (
        "id",
        "file"
    )
    extra = 0


class LoginAlertMessageAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = (
        "name",
        "published",
        "start_date",
        "end_date"
    )

admin.site.register(CertificateTemplate, CertificateTemplateAdmin)
admin.site.register(CertificateLogoFile, CertificateLogoFileAdmin)
admin.site.register(CertificateFrameFile, CertificateFrameFileAdmin)
admin.site.register(FooterLogoFile, FooterLogoFileAdmin)
admin.site.register(LoginAlertMessage, LoginAlertMessageAdmin)