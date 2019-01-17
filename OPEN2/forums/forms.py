from django import forms
from .models import Forum, Comment, Media

class NewMediaForm(forms.ModelForm):
  description = forms.CharField(
    widget = forms.Textarea(),
    max_length = 100,
    help_text = 'The max length for the forum description is 100.'
  )

  class Meta:
    model = Media
    fields = ['url', 'kind', 'description']

class NewForumForm(forms.ModelForm):
  name = forms.CharField(
    widget = forms.TextInput(),
    max_length = 30,
    help_text = 'The max length for the forum name is 30.'
  )
  description = forms.CharField(
    widget = forms.Textarea(),
    max_length = 100,
    help_text = 'The max length for the forum description is 100.'
  )

  class Meta:
    model = Forum
    fields = ['name', 'description']
    # exclude = ['author']