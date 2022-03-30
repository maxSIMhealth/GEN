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


class CertificateFrameFile(LogoFile):

    class Meta:
        verbose_name = _("certificate frame file")
        verbose_name_plural = _("certificate frame files")


class CertificateLogoFile(LogoFile):

    class Meta:
        verbose_name = _("certificate logo file")
        verbose_name_plural = _("certificate logos files")


class CertificateTemplate(models.Model):
    name = models.CharField(max_length=50)
    frame = models.ForeignKey(
        CertificateFrameFile,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        help_text=_("Image to be displayed as the certificate frame/border (page size: Letter).")
    )
    logos = models.ManyToManyField(
        CertificateLogoFile,
        blank=True,
        help_text=_("Logos to be displayed in the header portion of the certificate. Recommended size is 200x80 points.")
    )

    def __str__(self):
        return "%s" % self.name


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

