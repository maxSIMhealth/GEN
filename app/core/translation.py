from modeltranslation.translator import TranslationOptions, translator

from .models import HelpFaq


class HelpFaqTranslationOptions(TranslationOptions):
    fields = ("question", "answer")


translator.register(HelpFaq, HelpFaqTranslationOptions)
