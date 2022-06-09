from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import MoveToColumnsItem, TextBoxesTerm


class TextBoxesItemForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(TextBoxesItemForm, self).__init__(*args, **kwargs)
        # check if the instance exists (if it's a new object or not)
        if self.instance.pk is not None:
            # list only terms that are related to the same game as the item
            self.fields["correct_terms"].queryset = TextBoxesTerm.objects.filter(
                game=self.instance.game
            )

    def clean(self):
        super(TextBoxesItemForm, self).clean()
        correct_terms = self.cleaned_data.get("correct_terms")
        game = self.cleaned_data.get("game")

        if game.type == "MT":
            if correct_terms.__len__() > 1:
                raise ValidationError(
                    _("'Match term' game items can only have ONE answer.")
                )


class MoveToColumnsGroupForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(MoveToColumnsGroupForm, self).__init__(*args, **kwargs)
        # check if the instance exists (if it's a new object or not)
        if self.instance.pk is not None:
            # list only terms that are related to the same game as the item
            self.fields["source_items"].queryset = MoveToColumnsItem.objects.filter(
                game=self.instance.game
            )

            self.fields["choice1_items"].queryset = MoveToColumnsItem.objects.filter(
                game=self.instance.game
            )

            self.fields["choice2_items"].queryset = MoveToColumnsItem.objects.filter(
                game=self.instance.game
            )
