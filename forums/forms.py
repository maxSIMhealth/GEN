from django import forms
from django.core.validators import FileExtensionValidator
from .models import MediaFile, Forum, Comment, VideoFile
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


class NewForumForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(),
        max_length=100,
        label='Forum name',
        help_text='The max length for the forum name is 100.'
    )
    description = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'rows': 4
            }
        ),
        max_length=400,
        help_text='The max length for the forum description is 400.'
    )

    class Meta:
        model = Forum
        # fields = ['name', 'description']
        exclude = ['course', 'author', 'vote_score',
                   'num_vote_up', 'num_vote_down', 'media']


class NewMediaForm(forms.ModelForm):
    title = forms.CharField(
        widget=forms.TextInput(),
        max_length=100,
        label='Media name',
        help_text='The max length for the media title is 100.'
    )
    url = forms.URLField(
        widget=forms.URLInput(),
        help_text='Make sure that the URL is valid.'
    )

    class Meta:
        model = MediaFile
        # fields = ['name', 'description']
        exclude = ['author']


class NewCommentForm(forms.ModelForm):
    message = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'rows': 4
            }
        ),
        max_length=400,
        help_text='The max length for a comment is 400 characters.'
    )

    class Meta:
        model = Comment
        fields = ['message']


class UploadVideoForm(forms.ModelForm):
    description = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'rows': 4
            }
        ),
        max_length=255,
        help_text='The max length for a description is 255 characters.'
    )
    file = forms.FileField(
        help_text='Please upload a video file (mp4 or mov)',
        widget=forms.FileInput(
            attrs={'accept': 'video/mp4'}
        )
    )

    class Meta:
        model = VideoFile
        fields = ['title', 'description', 'file']

    helper = FormHelper()
    helper.add_input(Submit('submit', 'Submit', css_class='btn-primary'))
    helper.form_method = 'POST'
