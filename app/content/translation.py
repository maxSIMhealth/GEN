from modeltranslation.translator import TranslationOptions, register

from .models import ContentItem, ExternalObject, ImageFile, PdfFile


@register(ContentItem)
class ContentItemTranslationOptions(TranslationOptions):
    pass


@register(ImageFile)
class ImageFileTranslationOptions(TranslationOptions):
    pass


@register(PdfFile)
class PdfFileTranslationOptions(TranslationOptions):
    pass


@register(ExternalObject)
class ExternalObjectTranslationOptions(TranslationOptions):
    pass
