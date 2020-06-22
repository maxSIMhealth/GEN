from django import forms

from .models import Quiz, Section


class QuizAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(QuizAdminForm, self).__init__(*args, **kwargs)
        # check if the instance exists (if its a new object or not)
        if self.instance.pk is not None:
            # lists only sections that are related to the course
            self.fields["section"].queryset = Section.objects.filter(
                course=self.instance.course
            )
            self.fields["requirement"].queryset = Quiz.objects.exclude(
                pk=self.instance.pk
            ).filter(course=self.instance.course)
            # pass
