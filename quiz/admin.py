from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin
from django.contrib import admin
from django.forms import ModelForm
from import_export import resources
from import_export.admin import ExportActionMixin

# from django.contrib.admin.widgets import FilteredSelectMultiple

from .models import (
    Likert,
    LikertAnswer,
    LikertAttempt,
    MCAnswer,
    MCQuestion,
    MCQuestionAttempt,
    OpenEnded,
    OpenEndedAttempt,
    Question,
    QuestionAttempt,
    QuestionGroupHeader,
    Quiz,
    QuizScore,
)


def duplicate_quiz(modeladmin, request, queryset):
    for item in queryset:
        item.duplicate_quiz()


duplicate_quiz.short_description = "Duplicate selected quizzes"

# Classes AlwaysChangedModelForm and CheckerInline were based on:
# https://stackoverflow.com/questions/34355406/django-admin-not-saving-\
# pre-populated-inline-fields-which-are-left-in-their-init


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
    # https://django-admin-sortable2.readthedocs.io/en/latest/usage.html\
    # make-a-stacked-or-tabular-inline-view-sortable
    model = Question
    # include = ['quiz', 'content']
    exclude = [
        "explanation",
    ]
    extra = 0


class QuizAdmin(SortableAdminMixin, admin.ModelAdmin):
    # list_display = ("name", "course", "quiz_actions")
    list_display = ("name", "course")
    list_filter = ("course",)
    # search_fields = ('description', 'course', )
    inlines = (QuestionInline,)
    actions = [duplicate_quiz]
    save_as = True

    # filter_horizontal = ('questions', )

    # def get_urls(self):
    #     urls = super().get_urls()
    #     custom_urls = [path("copy/", self.duplicate_quiz)]
    #     return custom_urls + urls

    # def quiz_actions(self, obj):
    #     return format_html('<a class="button" href="#">Make a copy</a>',)


class QuizScoreAdmin(admin.ModelAdmin):
    list_display = ("student", "quiz", "course", "score")
    list_filter = ("quiz", "course", "student")

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

    list_display = ("content", "quiz", "created")
    list_filter = ("quiz",)
    search_fields = ("content", "explanation")
    # filter_horizontal = ('quiz',)


class MCQuestionAdmin(QuestionAdmin):
    """
    Class for multiple choice question editing
    """

    # list_display = ('quiz',
    #                 'content', 'created')
    # list_filter = ('quiz', 'content')
    fields = (
        "question_type",
        "content",
        "quiz",
        "explanation",
        "multiple_correct_answers",
    )
    inlines = [MCAnswerInline]

    # setting question_type value to Multiple Choice
    def get_form(self, request, obj=None, **kwargs):
        form = super(MCQuestionAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields["question_type"].initial = "M"
        return form


class MCAnswerAdmin(admin.ModelAdmin):
    list_display = ("question", "content", "correct")
    list_filter = ("question",)


class LikertAdmin(QuestionAdmin):
    """
    Class for likert question editing
    """

    fields = ("question_type", "content", "quiz")
    inlines = [LikertAnswerInline]
    # readonly_fields = ["question_type"]

    # setting question_type value to Likert
    def get_form(self, request, obj=None, **kwargs):
        form = super(LikertAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields["question_type"].initial = "L"
        return form


class LikertAnswerAdmin(admin.ModelAdmin):
    list_display = ("question", "scale_min", "scale_max")
    list_filter = ("question",)


class OpenEndedAdmin(QuestionAdmin):
    fields = ("question_type", "content", "quiz")

    # setting question_type value to Open Ended
    def get_form(self, request, obj=None, **kwargs):
        form = super(OpenEndedAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields["question_type"].initial = "O"
        return form


class QuestionAttemptResource(resources.ModelResource):
    class Meta:
        model = QuestionAttempt
        fields = (
            "id",
            "created",
            "student",
            "quiz__name",
            "course__name",
            "attempt_number",
        )


class QuestionAttemptAdmin(ExportActionMixin, admin.ModelAdmin):
    """
    Base class for quiz questions (likert, multiple choice, and open ended).
    All questions models follow the same naming pattern.
    """

    list_display = (
        "student",
        "course",
        "quiz",
        # "question",
        "attempt_number",
        "created",
    )
    # list_filter = ("course", "quiz", "question", "attempt_number")
    list_filter = ("course", "quiz", "attempt_number")
    resource_class = QuestionAttemptResource

    # search_fields = ('quiz', 'course', 'question', 'student')


class QuestionGroupHeaderAdmin(QuestionAdmin):
    # list_display = ('content',)
    # filter_horizontal = ('quiz',)
    fields = ("question_type", "content", "quiz")

    # setting question_type value to Group Header
    def get_form(self, request, obj=None, **kwargs):
        form = super(QuestionGroupHeaderAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields["question_type"].initial = "H"
        return form


# TODO: comment Question, MCAnswer, LikertAnswer (they can be edited using the
# question page and are only useful during testing and development)
admin.site.register(Quiz, QuizAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(MCQuestion, MCQuestionAdmin)
admin.site.register(MCQuestionAttempt, QuestionAttemptAdmin)
admin.site.register(MCAnswer, MCAnswerAdmin)
admin.site.register(QuizScore, QuizScoreAdmin)
admin.site.register(Likert, LikertAdmin)
# admin.site.register(LikertAnswer, LikertAnswerAdmin)
admin.site.register(LikertAttempt, QuestionAttemptAdmin)
admin.site.register(OpenEnded, OpenEndedAdmin)
admin.site.register(OpenEndedAttempt, QuestionAttemptAdmin)
admin.site.register(QuestionGroupHeader, QuestionGroupHeaderAdmin)
admin.site.register(QuestionAttempt, QuestionAttemptAdmin)
