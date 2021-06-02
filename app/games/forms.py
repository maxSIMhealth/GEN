from django import forms

from .models import TextBoxesItem, TextBoxesTerm


class TextBoxesItemForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(TextBoxesItemForm, self).__init__(*args, **kwargs)
        # check if the instance exists (if its a new object or not)
        if self.instance.pk is not None:
            # list only terms that are related to the same game as the item
            self.fields['correct_term'].queryset = TextBoxesTerm.objects.filter(game=self.instance.game)