from modeltranslation.translator import TranslationOptions, translator

from .models import Course, Section, SectionItem


class CourseTranslationOptions(TranslationOptions):
    fields = ("name", "description", "initial_section_name")


class SectionTranslationOptions(TranslationOptions):
    fields = ("name", "description", "completion_message")


class SectionItemTranslationOptions(TranslationOptions):
    fields = ("name", "description")


translator.register(Course, CourseTranslationOptions)
translator.register(Section, SectionTranslationOptions)
translator.register(SectionItem, SectionItemTranslationOptions)
