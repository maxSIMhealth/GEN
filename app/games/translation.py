from modeltranslation.translator import register, TranslationOptions

from .models import Game, TextBoxesGame, TextItem, TextBoxesTerm, TextBoxesItem,\
    MoveToColumnsGame, MoveToColumnsGroup, MoveToColumnsItem


@register(Game)
class GameTranslationOption(TranslationOptions):
    fields = ()


@register(TextItem)
class TextItemTranslationOption(TranslationOptions):
    fields = ('text', )


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
    fields = ('source_name','choice1_name','choice2_name')
