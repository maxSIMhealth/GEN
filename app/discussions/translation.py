from modeltranslation.translator import TranslationOptions, register

from .models import Discussion


@register(Discussion)
class DiscussionTranslationOptions(TranslationOptions):
    pass
