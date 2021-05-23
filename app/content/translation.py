from modeltranslation.translator import register, TranslationOptions

from .models import ContentItem, MatchColumnsGame, MatchColumnsItem


@register(ContentItem)
class ContentItemTranslationOptions(TranslationOptions):
    fields = ("content", )


@register(MatchColumnsGame)
class MatchColumnsGameTranslationOption(TranslationOptions):
    fields = ()


@register(MatchColumnsItem)
class MatchColumnsItemTranslationOption(TranslationOptions):
    fields = ("name", )
