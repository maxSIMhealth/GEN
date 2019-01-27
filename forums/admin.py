from django.contrib import admin
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple

from .models import Course, MediaFile, Forum, Comment
from quiz.models import Quiz, Question, MCQuestion, Answer, MCQuestionAttempt

class AnswerInline(admin.TabularInline):
    model = Answer


class QuizAdminForm(forms.ModelForm):
    """
        below is from
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
    list_display = ('student', 'course', 'quiz', 'question' )
    list_filter = ('course', 'quiz')

    search_fields = ('quiz', 'course', 'question')
    # filter_horizontal = ('student',)


class CourseAdmin(admin.ModelAdmin):
    # fields = ('name', 'students')
    filter_horizontal = ('students',)


admin.site.register(Course, CourseAdmin)
admin.site.register(MediaFile)
admin.site.register(Forum)
admin.site.register(Comment)
admin.site.register(Quiz, QuizAdmin)
# admin.site.register(Question)
admin.site.register(MCQuestion, MCQuestionAdmin)
admin.site.register(MCQuestionAttempt, MCQuestionAttempAdmin)
# admin.site.register(Answer)