from django.contrib import admin
from django import forms
from django.forms import ModelForm
from django.contrib.admin.widgets import FilteredSelectMultiple
from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin

from .models import Quiz, Question, MCQuestion, MCAnswer, MCQuestionAttempt, \
    QuizScore, Likert, LikertAnswer, LikertAttempt, OpenEnded, OpenEndedAttempt, \
    QuestionGroupHeader, QuestionAttempt


# Classes AlwaysChangedModelForm and CheckerInline were based on:
# https://stackoverflow.com/questions/34355406/django-admin-not-saving-pre-populated-inline-fields-which-are-left-in-their-init

class AlwaysChangedModelForm(ModelForm):
    """
    Should returns True if data differs from initial.
    By always returning true even unchanged inlines will get validated and saved.
    """

    def has_changed(self):
        return True


class CheckerInline(admin.StackedInline):
    """
    Base class for checker inlines
    """

    extra = 1  # defines the initial number of fields
    form = AlwaysChangedModelForm


class QuestionInline(SortableInlineAdminMixin, admin.TabularInline):
    """
    Class for creating a sortable inline tabular layout for questions.
    """
    # Tip: admin.TabularInline can be switched with admin.StackedInline
    # Documentation at
    # https://django-admin-sortable2.readthedocs.io/en/latest/usage.html#make-a-stacked-or-tabular-inline-view-sortable
    model = Question
    # include = ['quiz', 'content']
    exclude = ['explanation', ]
    extra = 0


class QuizAdmin(admin.ModelAdmin):
    list_display = ('name', 'course', )
    list_filter = ('course', )
    # search_fields = ('description', 'course', )
    inlines = (QuestionInline,)

    # filter_horizontal = ('questions', )


class QuizScoreAdmin(admin.ModelAdmin):
    list_display = ('student', 'quiz', 'course', 'score')
    list_filter = ('quiz', 'course', 'student')

    # search_fields = ('student', 'quiz', 'course')
    # filter_horizontal = ('student',)


class MCAnswerInline(SortableInlineAdminMixin, admin.TabularInline):
    """
    Class to show multiple choice answers inline (tabular)
    """

    model = MCAnswer
    extra = 0


class LikertAnswerInline(CheckerInline):
    """
    Class to show likert answers inline (stacked), and based on
    CheckerInline to always save while submitting/creating a Likert
    object (even if the LikertAnswer fields are using the default values)
    """

    model = LikertAnswer


class QuestionAdmin(admin.ModelAdmin):
    """
    Base class for questions admin layout (editing).
    """
    list_display = ('content', 'quiz', 'created')
    list_filter = ('quiz', 'content')
    search_fields = ('content', 'explanation')
    # filter_horizontal = ('quiz',)


class MCQuestionAdmin(QuestionAdmin):
    """
    Class for multiple choice question editing
    """
    # list_display = ('quiz',
    #                 'content', 'created')
    # list_filter = ('quiz', 'content')
    fields = ('content', 'quiz', 'explanation')
    inlines = [MCAnswerInline]


class MCAnswerAdmin(admin.ModelAdmin):
    list_display = ('question', 'content', 'correct')
    list_filter = ('question', )


class LikertAdmin(QuestionAdmin):
    """
    Class for likert question editing
    """
    fields = ('content', 'quiz')
    inlines = [LikertAnswerInline]


class LikertAnswerAdmin(admin.ModelAdmin):
    list_display = ('question', 'scale_min', 'scale_max')
    list_filter = ('question',)


class OpenEndedAdmin(QuestionAdmin):
    fields = ('content', 'quiz')


class QuestionAttemptAdmin(admin.ModelAdmin):
    """
    Base class for quiz questions (likert, multiple choice, and open ended).
    All questions models follow the same naming pattern.
    """
    list_display = ('student', 'course', 'quiz',
                    'question', 'attempt_number', 'created')
    list_filter = ('course', 'quiz', 'question', 'attempt_number')

    # search_fields = ('quiz', 'course', 'question', 'student')


class QuestionGroupHeaderAdmin(QuestionAdmin):
    # list_display = ('content',)
    # filter_horizontal = ('quiz',)
    fields = ('content', 'quiz')


# TODO: comment Question, MCAnswer, LikertAnswer (they can be edited using the
# question page and are only useful during testing and development)
admin.site.register(Quiz, QuizAdmin)
# admin.site.register(Question, QuestionAdmin)
admin.site.register(MCQuestion, MCQuestionAdmin)
admin.site.register(MCQuestionAttempt, QuestionAttemptAdmin)
# admin.site.register(MCAnswer, MCAnswerAdmin)
admin.site.register(QuizScore, QuizScoreAdmin)
admin.site.register(Likert, LikertAdmin)
# admin.site.register(LikertAnswer, LikertAnswerAdmin)
admin.site.register(LikertAttempt, QuestionAttemptAdmin)
admin.site.register(OpenEnded, OpenEndedAdmin)
admin.site.register(OpenEndedAttempt, QuestionAttemptAdmin)
admin.site.register(QuestionGroupHeader, QuestionGroupHeaderAdmin)
admin.site.register(QuestionAttempt)
