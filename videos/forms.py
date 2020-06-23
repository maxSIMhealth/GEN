# from django.core.validators import FileExtensionValidator

from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Button, Fieldset, Layout, Submit
from django import forms
from django.utils.translation import gettext_lazy as _

from courses.models import Section
from .models import VideoFile


class UploadVideoForm(forms.ModelForm):
    description = forms.CharField(
        label=_("Description"),
        widget=forms.Textarea(attrs={"rows": 4}),
        max_length=400,
        help_text=_("The max length for a description is 400 characters."),
    )
    file = forms.FileField(
        label=_("File"),
        widget=forms.FileInput(attrs={"accept": "video/mp4"}),
        help_text=_("Please upload a video file (mp4 or mov)"),
    )

    class Meta:
        model = VideoFile
        fields = ["name", "description", "file"]

    def __init__(self, *args, **kwargs):
        super(UploadVideoForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            # FIXME: find a new to get first fieldset value (the legend) to be
            # wrapped in a div
            Fieldset(
                # "Upload a new video",
                "",
                "name",
                "description",
                "file",
            ),
            FormActions(
                Submit("submit", _("Submit"), css_class="btn btn-primary"),
                # Button("cancel", _("Cancel"), css_class="btn btn-secondary"),
                Button(
                    "cancel",
                    _("Cancel"),
                    css_class="btn btn-secondary",
                    onclick="window.location.href = window.history.go(-1); return false;",
                ),
            ),
        )
        self.helper.form_method = "POST"


class VideoFileAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(VideoFileAdminForm, self).__init__(*args, **kwargs)
        # check if the instance exists (if its a new object or not)
        if self.instance.pk is not None:
            # lists only sections that are related to the course
            self.fields["section"].queryset = Section.objects.filter(
                course=self.instance.course
            )
