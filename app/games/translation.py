from modeltranslation.translator import TranslationOptions, register

from .models import (
    Game,
    MatchTermsGame,
    MoveToColumnsGame,
    MoveToColumnsGroup,
    MoveToColumnsItem,
    TextBoxesGame,
    TextBoxesItem,
    TextBoxesTerm,
    TextItem,
)


@register(Game)
class GameTranslationOption(TranslationOptions):
    fields = ()


@register(TextItem)
class TextItemTranslationOption(TranslationOptions):
    fields = ("text",)


@register(TextBoxesGame)
class TextBoxesGameTranslationOption(TranslationOptions):
    fields = ()


@register(TextBoxesTerm)
class TextBoxesTermTranslationOption(TranslationOptions):
    fields = ()


@register(TextBoxesItem)
class TextBoxesItemTranslationOption(TranslationOptions):
    fields = ()


@register(MoveToColumnsGame)
class MoveToColumnsGameTranslationOption(TranslationOptions):
    fields = ()


@register(MoveToColumnsItem)
class MoveToColumnsItemTranslationOption(TranslationOptions):
    fields = ()


@register(MoveToColumnsGroup)
class MoveToColumnsGroupTranslationOption(TranslationOptions):
    fields = ("source_name", "choice1_name", "choice2_name")


@register(MatchTermsGame)
class MatchTermsGameTranslationOption(TranslationOptions):
    fields = ()
