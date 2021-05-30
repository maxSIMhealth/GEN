from modeltranslation.translator import register, TranslationOptions

from .models import ContentItem


@register(ContentItem)
class ContentItemTranslationOptions(TranslationOptions):
    fields = ("content", )

