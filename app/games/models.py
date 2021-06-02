from django.db import models
from django.utils.translation import gettext_lazy as _
from courses.models import SectionItem


class GameObjectsManager(models.Manager):
    def get_queryset(self):
        """
        Returns all games types
        """
        qs = super().get_queryset().all()
        return qs


class MoveToColumnsManager(models.Manager):
    def get_queryset(self):
        """
        Returns only games of type "MC" (Move to Columns)
        """
        qs = super().get_queryset().filter(type='MC')
        return qs


class MatchTermsManager(models.Manager):
    def get_queryset(self):
        """
        Returns only games of type "MT" (Match terms)
        """
        qs = super().get_queryset().filter(type='MT')
        return qs


class TextBoxesManager(models.Manager):
    def get_queryset(self):
        """
        Returns only games of type "TB" (Text boxes)
        """
        qs = super().get_queryset().filter(type='TB')
        return qs


class Game(SectionItem):
    GAME_TYPES = [
        ('MC', _('Move to columns')),
        ('MT', _('Match terms')),
        ('TB', _('Text boxes')),
    ]
    type = models.CharField(
        _('game type'), max_length=2, choices=GAME_TYPES
    )

    # override objects variable
    objects = GameObjectsManager()
    move_columns = MoveToColumnsManager()
    match_terms = MatchTermsManager()
    text_boxes = TextBoxesManager()


class TextItem(models.Model):
    text = models.CharField(
        _('text'),
        max_length=100,
        unique=False,
        help_text=_('Item text description (max 100 characters)'),
    )
    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE
    )

    class Meta:
        abstract = True

    def __str__(self):
        return f'ID {self.pk} - {self.text}'


class TextBoxesGame(Game):
    class Meta:
        verbose_name = 'Complete the text boxes game'
        verbose_name_plural = 'Complete the text boxes games'
        proxy = True


class TextBoxesTerm(TextItem):
    custom_order = models.PositiveIntegerField(
        _('custom order'), default=0, blank=False, null=False
    )

    class Meta:
        ordering = ['custom_order']

    def __str__(self):
        return f'ID {self.pk} - {self.text}'


class TextBoxesItem(TextItem):
    text = models.TextField(
        _('text'),
        max_length=400,
        unique=False,
        help_text=_('Item text description (max 400 characters)'),
    )
    correct_term = models.ForeignKey(
        TextBoxesTerm,
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )
    custom_order = models.PositiveIntegerField(
        _('custom order'), default=0, blank=False, null=False
    )

    class Meta:
        ordering = ['custom_order']

    def __str__(self):
        return f'ID {self.pk} - {self.text}'


class MoveToColumnsGame(Game):
    class Meta:
        verbose_name = 'Move to columns game'
        verbose_name_plural = 'Move to columns games'
        proxy = True


class MoveToColumnsItem(TextItem):
    game = models.ForeignKey(
        MoveToColumnsGame,
        on_delete=models.CASCADE
    )
    custom_order = models.PositiveIntegerField(
        _('custom order'), default=0, blank=False, null=False
    )

    class Meta:
        ordering = ['custom_order']

    def __str__(self):
        return f'ID {self.pk} - {self.text}'


class MoveToColumnsGroup(models.Model):
    game = models.OneToOneField(
        MoveToColumnsGame,
        on_delete=models.PROTECT,
        related_name='columns'
    )
    source_name = models.CharField(
        _("source column name"),
        max_length=100,
        default='Source column',
        unique=False,
        help_text=_("Source column name"),
    )
    source_items = models.ManyToManyField(
        MoveToColumnsItem,
        related_name="source_column_items",
        verbose_name="source column items",
        help_text=_("List of items that are part of this column.")
    )
    choice1_name = models.CharField(
        _("choice 1 column name"),
        max_length=100,
        default="Choice 1 column",
        unique=False,
        help_text=_("Choice 1 column name"),
    )
    choice1_items = models.ManyToManyField(
        MoveToColumnsItem,
        related_name="choice1_column_items",
        verbose_name="choice 1 column items",
        help_text=_("List of items that are part of this column.")
    )
    choice2_name = models.CharField(
        _("choice 1 column name"),
        max_length=100,
        default="Choice 2 column",
        unique=False,
        help_text=_("Choice 2 column name"),
    )
    choice2_items = models.ManyToManyField(
        MoveToColumnsItem,
        related_name="choice2_column_items",
        verbose_name="choice 2 column items",
        help_text=_("List of items that are part of this column.")
    )

    class Meta:
        verbose_name = 'Move to columns game content'
        verbose_name_plural = 'Move to columns games content'


class MatchTermsGame(Game):
    class Meta:
        verbose_name = 'Match terms game'
        verbose_name_plural = 'Match terms games'
        proxy = True
