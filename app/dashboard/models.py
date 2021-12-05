from django.core.exceptions import ValidationError
from django.db import models
from django.db.utils import IntegrityError
from django.db.models import Q
from django.db.models.constraints import UniqueConstraint
from django.utils.translation import gettext_lazy as _
from tinymce import HTMLField


class DashboardSetting(models.Model):
    name = models.CharField(
        _("name"),
        max_length=150,
        unique=True,
        help_text=_("Dashboard name (max 150 characters)."),
    )
    image = models.ImageField(
        _("image"),
        upload_to='uploads/dashboard/',
        blank=True,
        null=True,
        help_text=_("'Hero' image that will be displayed on top portion of the dashboard (home page).")
    )
    description = HTMLField(
        blank=True,
        null=True
    )
    instructions = HTMLField(
        blank=True,
        null=True
    )
    active = models.BooleanField(
        _("active"),
        help_text=_("Set this setting as the active one. **WARNING**: only one setting can be set as active.")
    )

    def __str__(self):
        output = f'ID {self.pk} - {self.name}'
        return output

    def save(self, *args, **kwargs):
        try:
            return super(DashboardSetting, self).save(*args, **kwargs)
        except IntegrityError:
            raise ValidationError('Only one dashboard setting can be set as active.')

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['active'],
                condition=Q(active=True),
                name='unique_active_dashboard')
        ]


