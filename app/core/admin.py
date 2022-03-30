from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin

from core.models import CertificateLogoFile, FooterLogoFile, CertificateTemplate, CertificateFrameFile


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


admin.site.register(CertificateTemplate, CertificateTemplateAdmin)
admin.site.register(CertificateLogoFile, CertificateLogoFileAdmin)
admin.site.register(CertificateFrameFile, CertificateFrameFileAdmin)
admin.site.register(FooterLogoFile, FooterLogoFileAdmin)