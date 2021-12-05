from modeltranslation.translator import TranslationOptions, translator

from .models import DashboardSetting

class DashboardTranslationOptions(TranslationOptions):
    fields = ("name", "description", "instructions")

translator.register(DashboardSetting, DashboardTranslationOptions)