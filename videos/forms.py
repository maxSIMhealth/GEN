from django import forms

# from django.core.validators import FileExtensionValidator

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Div
from crispy_forms.bootstrap import FormActions

from .models import VideoFile


class UploadVideoForm(forms.ModelForm):
    description = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 4}),
        max_length=400,
        help_text="The max length for a description is 400 characters.",
    )
    file = forms.FileField(
        help_text="Please upload a video file (mp4 or mov)",
        widget=forms.FileInput(attrs={"accept": "video/mp4"}),
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
                Submit("submit", "Submit", css_class="btn btn-primary"),
                Submit(
                    "submit",
                    "Cancel",
                    css_class="btn btn-secondary",
                    formnovalidate="formnovalidate",
                ),
            ),
        )
        self.helper.form_method = "POST"
