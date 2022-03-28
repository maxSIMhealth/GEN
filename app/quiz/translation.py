from modeltranslation.translator import register, TranslationOptions

from .models import (
    Likert,
    LikertAnswer,
    MCAnswer,
    MCQuestion,
    OpenEnded,
    Question,
    QuestionGroupHeader,
    Quiz,
)


@register(Question)
class QuestionTranslationOptions(TranslationOptions):
    fields = ("content", "feedback")


@register(LikertAnswer)
class LikertAnswerTranslationOptions(TranslationOptions):
    fields = ("legend",)


@register(MCAnswer)
class MCAnswerTranslationOptions(TranslationOptions):
    fields = ("content",)


@register(Likert)
class LikertTranslationOptions(TranslationOptions):
    pass


@register(MCQuestion)
class MCQuestionTranslationOptions(TranslationOptions):
    pass


@register(OpenEnded)
class OpenEndedTranslationOptions(TranslationOptions):
    pass


@register(QuestionGroupHeader)
class QuestionGroupHeaderTranslationOptions(TranslationOptions):
    pass


@register(Quiz)
class QuizTranslationOptions(TranslationOptions):
    pass
