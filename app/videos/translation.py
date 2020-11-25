from modeltranslation.translator import TranslationOptions, translator

from .models import VideoFile


class VideoFileTranslationOptions(TranslationOptions):
    pass


translator.register(VideoFile, VideoFileTranslationOptions)
