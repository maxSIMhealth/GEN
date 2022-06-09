from content.models import SectionItem
from core.support_methods import user_directory_path_not_random
from model_utils.models import TimeStampedModel
from scorm.support_methods import (
    delete_from_scorm_cloud,
    delete_registration_from_scorm_cloud,
    enroll_learners,
    export_to_scorm_cloud,
    get_registration_details,
)
from upload_validator import FileTypeValidator

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from GEN.storage_backends import PrivateMediaStorage


class ScormPackage(SectionItem):

    file = models.FileField(
        _("SCORM package"),
        upload_to=user_directory_path_not_random,
        storage=PrivateMediaStorage(),
        help_text=_("Format accepted: zip."),
        validators=[FileTypeValidator(allowed_types=["application/zip"])],
    )
    package_id = models.CharField(
        unique=True,
        blank=True,
        max_length=255,
        help_text=_(
            "Identifier used by SCORM Cloud to refer to the package (note "
            "that  SCORM Cloud uses the terms 'package' and 'course' "
            "interchangeably)."
        ),
    )

    def __str__(self):
        return f"{self.name}"

    def save(self, *args, **kwargs):
        self.item_type = SectionItem.SECTION_ITEM_SCORM
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.file.delete()
        delete_from_scorm_cloud(self)
        super().delete(*args, **kwargs)  # Call the "real" delete() method.

    def enroll_learners(self, *args, **kwargs):
        # TODO: this should be done when a participant gets enrolled into a course/module OR when a new SCORM package gets added into a course/module
        enroll_learners(self)

    def create_registration(self, registration_id, learner, *args, **kwargs):
        """
        Create object that links the learner, SCORM Cloud registration id
        and the SCORM package.

        Args:
            registration_id:
            learner:
            *args:
            **kwargs:

        Returns: ScormRegistration object.

        """

        new_registration = ScormRegistration(
            registration_id=registration_id, learner=learner, package_object=self
        )

        new_registration.save()

        return new_registration

    def export_to_scorm_cloud(self, request):
        export_to_scorm_cloud(self, request)

    def clean(self):
        errors_dict = {}

        if self.published and not self.package_id:
            errors_dict["published"] = _(
                "You need to use the action 'Export into ScormCloud' below before being able to set item as 'Published'"
            )

        if len(errors_dict) > 0:
            raise ValidationError(errors_dict)
        else:
            return super().clean()


class ScormRegistration(TimeStampedModel):
    registration_id = models.CharField(
        unique=True,
        max_length=255,
    )
    learner = models.ForeignKey(User, on_delete=models.PROTECT)
    package_object = models.ForeignKey(ScormPackage, on_delete=models.PROTECT)
    activity_completion = models.CharField(max_length=255, blank=True)
    activity_success = models.CharField(max_length=255, blank=True)
    attempts = models.IntegerField(
        blank=True,
        null=True,
    )
    completion_amount = models.FloatField(
        blank=True,
        null=True,
    )
    score = models.FloatField(
        blank=True,
        null=True,
    )
    time_tracked = models.TimeField(
        blank=True,
        null=True,
    )
    title = models.CharField(
        max_length=500,
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"{self.registration_id}"

    def delete(self, *args, **kwargs):
        delete_registration_from_scorm_cloud(self)
        super().delete(*args, **kwargs)

    def update_details(self, *args, **kwargs):
        # TODO: test fail condition
        result = get_registration_details(self)

        details = result.activity_details
        self.activity_completion = details.activity_completion
        self.activity_success = details.activity_success
        self.attempts = details.attempts
        self.completion_amount = details.completion_amount.scaled
        self.title = details.title

        if details.score:
            self.score = details.score.scaled

        # self.time_tracked = details.time_tracked
        self.save(
            update_fields=[
                "activity_completion",
                "activity_success",
                "attempts",
                "completion_amount",
                "title",
                "score",
            ]
        )
