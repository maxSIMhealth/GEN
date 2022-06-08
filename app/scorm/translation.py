from modeltranslation.translator import TranslationOptions, register

from .models import ScormPackage


@register(ScormPackage)
class ScormObjectTranslationOptions(TranslationOptions):
    pass
