from modeltranslation.translator import TranslationOptions, translator

from .models import Quiz


class QuizTranslationOptions(TranslationOptions):
    pass


translator.register(Quiz, QuizTranslationOptions)
