from modeltranslation.translator import TranslationOptions, translator

from .models import DashboardSettings

class DashboardTranslationOptions(TranslationOptions):
    fields = ("name", "description", "instructions")

translator.register(DashboardSettings, DashboardTranslationOptions)