from modeltranslation.translator import register, TranslationOptions

from .models import ContentItem, ImageFile


@register(ContentItem)
class ContentItemTranslationOptions(TranslationOptions):
    fields = ("content",)


@register(ImageFile)
class ImageFileTranslationOptions(TranslationOptions):
    pass
