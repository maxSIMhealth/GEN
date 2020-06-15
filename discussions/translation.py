from modeltranslation.translator import register, TranslationOptions

from .models import Discussion


@register(Discussion)
class DiscussionTranslationOptions(TranslationOptions):
    pass
