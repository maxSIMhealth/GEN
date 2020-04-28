from django.contrib import admin
from django import forms
from django.forms import ModelForm
from django.contrib.admin.widgets import FilteredSelectMultiple

from .models import Quiz, Question, MCQuestion, Answer, MCQuestionAttempt, \
    QuizScore, Likert, LikertAnswer, LikertAttempt, OpenEnded, OpenEndedAttempt


# Classes AlwaysChangedModelForm and CheckerInline were based on:
# https://stackoverflow.com/questions/34355406/django-admin-not-saving-pre-populated-inline-fields-which-are-left-in-their-init

class AlwaysChangedModelForm(ModelForm):
    """ Should returns True if data differs from initial.
        By always returning true even unchanged inlines will get validated and saved."""

    def has_changed(self):
        return True


class CheckerInline(admin.StackedInline):
    """ Base class for checker inlines """
    extra = 1  # defines the initial number of fields
    form = AlwaysChangedModelForm


class AnswerInline(admin.TabularInline):
    """Model to show multiple choice answers inline (tabular)"""
    model = Answer


class LikertAnswerInline(CheckerInline):
    """Model to show likert answers inline (stacked), and based on
    CheckerInline to always save while submitting/creating a Likert
    object (even if the LikertAnswer fields are using the default values) """
    model = LikertAnswer


class QuizAdminForm(forms.ModelForm):
    """
        part of the code below is from
        http://stackoverflow.com/questions/11657682/
        django-admin-interface-using-horizontal-filter-with-
        inline-manytomany-field
    """

    class Meta:
        model = Quiz
        exclude = []

    questions = forms.ModelMultipleChoiceField(
        queryset=Question.objects.all().select_subclasses(),
        required=False,
        label="Questions",
        widget=FilteredSelectMultiple(
            verbose_name="Questions",
            is_stacked=False))

    def __init__(self, *args, **kwargs):
        super(QuizAdminForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['questions'].initial = \
                self.instance.questions.all().select_subclasses()

    def save(self, commit=True):
        quiz = super(QuizAdminForm, self).save(commit=False)
        quiz.save()
        quiz.questions.set(self.cleaned_data['questions'])
        self.save_m2m()
        return quiz


class QuizAdmin(admin.ModelAdmin):
    form = QuizAdminForm

    list_display = ('name', 'course', )
    list_filter = ('course', )
    search_fields = ('description', 'course', )

    # filter_horizontal = ('questions', )


class MCQuestionAdmin(admin.ModelAdmin):
    list_display = ('content', )
    fields = ('content', 'quiz', 'explanation')

    search_fields = ('content', 'explanation')
    filter_horizontal = ('quiz',)

    inlines = [AnswerInline]


class MCQuestionAttempAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'quiz', 'question', 'created')
    list_filter = ('course', 'quiz')

    search_fields = ('quiz', 'course', 'question')
    # filter_horizontal = ('student',)


class QuizScoreAdmin(admin.ModelAdmin):
    list_display = ('student', 'quiz', 'course', 'score')
    list_filter = ('quiz', 'course', 'student')

    # search_fields = ('student', 'quiz', 'course')
    # filter_horizontal = ('student',)


class LikertAdmin(admin.ModelAdmin):
    list_display = ('content', )
    fields = ('content', 'quiz', 'explanation')

    search_fields = ('content', 'explanation')
    filter_horizontal = ('quiz', )

    inlines = [LikertAnswerInline]


class LikertAnswerAdmin(admin.ModelAdmin):
    pass


class LikertAttempAdmin(admin.ModelAdmin):
    list_display = ('student', 'likert', 'attempt_number', 'created')
    list_filter = ('student', 'likert', 'attempt_number')

    search_fields = ('student', 'likert', )


class OpenEndedAdmin(admin.ModelAdmin):
    pass


class OpenEndedAttempAdmin(admin.ModelAdmin):
    pass


admin.site.register(Quiz, QuizAdmin)
# admin.site.register(Question)
admin.site.register(MCQuestion, MCQuestionAdmin)
admin.site.register(MCQuestionAttempt, MCQuestionAttempAdmin)
admin.site.register(Answer)
admin.site.register(QuizScore, QuizScoreAdmin)
admin.site.register(Likert, LikertAdmin)
admin.site.register(LikertAnswer, LikertAnswerAdmin)
admin.site.register(LikertAttempt, LikertAttempAdmin)
admin.site.register(OpenEnded, OpenEndedAdmin)
admin.site.register(OpenEndedAttempt, OpenEndedAttempAdmin)
