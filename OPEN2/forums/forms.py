from django import forms
from .models import Forum, Comment

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
  url = forms.URLField(
    widget = forms.URLInput(),
    help_text = 'Make sure that the URL is valid.'
  )

  class Meta:
    model = Forum
    # fields = ['name', 'description']
    exclude = ['author']

class NewCommentForm(forms.ModelForm):
  message = forms.CharField(
    widget = forms.Textarea(
      attrs= {
        'rows': 4
      }
    ),
    max_length = 400,
    help_text = 'The max length for a comment is 400.'
  )

  class Meta:
    model = Comment
    fields = ['message']