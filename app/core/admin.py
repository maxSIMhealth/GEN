from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin

from core.models import CertificateLogoFile, FooterLogoFile


class CertificateLogoFileAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = (
        "id",
        "file"
    )
    extra = 0

class FooterLogoFileAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = (
        "id",
        "file"
    )
    extra = 0


admin.site.register(CertificateLogoFile, CertificateLogoFileAdmin)
admin.site.register(FooterLogoFile, FooterLogoFileAdmin)