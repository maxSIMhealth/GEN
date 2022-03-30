from django.db import models
from django.utils.translation import gettext_lazy as _

class LogoFile(models.Model):
    file = models.ImageField(
        _("file"),
        upload_to='uploads/logos/'
    )

    def __str__(self):
        output = "{0}".format(self.file.name.split('/')[-1])
        return output


class CertificateLogoFile(LogoFile):
    custom_order = models.PositiveIntegerField(
        _("custom order"), default=0, blank=False, null=False
    )

    class Meta:
        verbose_name = _("certificate logo file")
        verbose_name_plural = _("certificate logos files")
        ordering = ["custom_order"]


class FooterLogoFile(LogoFile):
    description = models.CharField(
        _("description"),
        max_length=255,
        help_text=_("Brief description of the logo (max 255 characters)"),
    )
    url = models.URLField(
        max_length=255,
        help_text=_("URL of the destination site when the user clicks on the logo."),
    )
    custom_order = models.PositiveIntegerField(
        _("custom order"), default=0, blank=False, null=False
    )

    class Meta:
        verbose_name = _("footer logo file")
        verbose_name_plural = _("footer logos files")
        ordering = ["custom_order"]

