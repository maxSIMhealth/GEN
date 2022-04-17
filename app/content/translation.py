from modeltranslation.translator import TranslationOptions, register

from .models import ContentItem, ImageFile, PdfFile


@register(ContentItem)
class ContentItemTranslationOptions(TranslationOptions):
    fields = ("content",)


@register(ImageFile)
class ImageFileTranslationOptions(TranslationOptions):
    pass


@register(PdfFile)
class PdfFileTranslationOptions(TranslationOptions):
    pass
