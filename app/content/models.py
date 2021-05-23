from django.db import models
from model_utils.models import TimeStampedModel
from django.utils.translation import gettext_lazy as _
from courses.models import SectionItem
from tinymce.models import HTMLField


class ContentItem(SectionItem):
    content = HTMLField(
        blank=True,
        null=True
    )


class MatchColumnsItem(models.Model):
    name = models.CharField(
        _("name"),
        max_length=100,
        unique=False,
        help_text=_("Item name"),
    )

    def __str__(self):
        return f'ID {self.pk} - {self.name}'


class MatchColumnsGame(ContentItem):
    source_column_name = models.CharField(
        _("source column name"),
        max_length=100,
        default='Source column',
        unique=False,
        help_text=_("Source column name"),
    )
    source_column_items = models.ManyToManyField(
        MatchColumnsItem,
        related_name="source_column_items",
        verbose_name="source column items",
        help_text=_("List of items that are part of this column.")
    )
    choice1_column_name = models.CharField(
        _("choice 1 column name"),
        max_length=100,
        default="Choice 1 column",
        unique=False,
        help_text=_("Choice 1 column name"),
    )
    choice1_column_items = models.ManyToManyField(
        MatchColumnsItem,
        related_name="choice1_column_items",
        verbose_name="choice 1 column items",
        help_text=_("List of items that are part of this column.")
    )
    choice2_column_name = models.CharField(
        _("choice 1 column name"),
        max_length=100,
        default="Choice 2 column",
        unique=False,
        help_text=_("Choice 2 column name"),
    )
    choice2_column_items = models.ManyToManyField(
        MatchColumnsItem,
        related_name="choice2_column_items",
        verbose_name="choice 2 column items",
        help_text=_("List of items that are part of this column.")
    )

    def __str__(self):
        return f'ID {self.pk} - {self.name}'
