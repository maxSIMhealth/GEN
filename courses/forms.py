from django import forms

from .models import Section


class SectionInlineForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SectionInlineForm, self).__init__(*args, **kwargs)
        # check if the instance exists (if its a new object or not)
        if self.instance.pk is not None:
            self.fields["requirement"].queryset = Section.objects.filter(
                course=self.instance.course
            )
