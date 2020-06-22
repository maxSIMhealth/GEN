from django import forms

from .models import Section


class SectionAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SectionAdminForm, self).__init__(*args, **kwargs)
        # check if the instance exists (if its a new object or not)
        if self.instance.pk is not None:
            # lists only sections that are related to the course and
            # exclude itself from requirement and output
            self.fields["requirement"].queryset = Section.objects.exclude(
                pk=self.instance.pk
            ).filter(course=self.instance.course)
            # only upload sections can have an output, which must be a discussion section
            if self.instance.section_type == "U":
                self.fields["section_output"].queryset = Section.objects.exclude(
                    pk=self.instance.pk
                ).filter(course=self.instance.course, section_type="D")
            else:
                # return an empty queryset
                self.fields["section_output"].queryset = Section.objects.none()
