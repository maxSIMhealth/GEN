from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Button, Fieldset, Layout, Submit
from videos.models import VideoFile

from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Comment, Discussion


class NewDiscussionForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(),
        max_length=100,
        label=_("Discussion board name"),
        help_text=_("The max length for the discussion board name is 100."),
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 4}),
        max_length=400,
        label=_("Description"),
        help_text=_("The max length for the discussion board description is 400."),
    )

    class Meta:
        model = Discussion
        fields = ["name", "description", "video"]
        # exclude = ['course', 'vote_score',
        #    'num_vote_up', 'num_vote_down']

    def __init__(self, course, *args, **kwargs):
        super(NewDiscussionForm, self).__init__(*args, **kwargs)
        self.fields["video"].queryset = VideoFile.objects.filter(course=course)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            # FIXME: find a new to get first fieldset value (the legend) to be
            # wrapped in a div
            Fieldset(
                # "Create new discussion board",
                "",
                "name",
                "description",
                "video",
            ),
            FormActions(
                Submit("submit", _("Submit"), css_class="btn btn-primary"),
                Button(
                    "cancel",
                    _("Cancel"),
                    css_class="btn btn-secondary",
                    onclick="window.location.href = window.history.go(-1); return false;",
                ),
                # Submit(
                #     "submit",
                #     "Cancel",
                #     css_class="btn btn-danger",
                #     formnovalidate="formnovalidate",
                # ),
            ),
        )
        self.helper.form_method = "POST"


# class NewMediaForm(forms.ModelForm):
#     title = forms.CharField(
#         widget=forms.TextInput(),
#         max_length=100,
#         label='Media name',
#         help_text='The max length for the media title is 100.'
#     )
#     url = forms.URLField(
#         widget=forms.URLInput(),
#         help_text='Make sure that the URL is valid.'
#     )

#     class Meta:
#         model = MediaFile
#         # fields = ['name', 'description']
#         exclude = ['author']


class NewCommentForm(forms.ModelForm):
    message = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 4}),
        max_length=400,
        label=_("Message"),
        help_text=_("The max length for a comment is 400 characters."),
    )

    class Meta:
        model = Comment
        fields = ["message"]
