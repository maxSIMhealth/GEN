from django import forms

from .models import Section


class SectionAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SectionAdminForm, self).__init__(*args, **kwargs)
        # check if the instance exists (if its a new object or not)
        if self.instance.pk is not None:
            # lists only sections that are related to the course
            self.fields["requirement"].queryset = Section.objects.filter(
                course=self.instance.course
            )
            self.fields["section_output"].queryset = Section.objects.filter(
                course=self.instance.course
            )
