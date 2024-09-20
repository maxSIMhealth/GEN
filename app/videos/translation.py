from modeltranslation.translator import TranslationOptions, translator

from .models import VideoFile


class VideoFileTranslationOptions(TranslationOptions):
    fields = ("subtitle", )


translator.register(VideoFile, VideoFileTranslationOptions)
